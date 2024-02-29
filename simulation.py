from collections import deque
import dataclasses
import enum
import logging
import random
from typing import Union


# logging.basicConfig(level="INFO", format = "%(levelname)s %(message)s")
# logging.basicConfig(level="DEBUG", format = "%(levelname)s %(message)s")


class Floor(enum.IntEnum):
    GROUND = 1
    F2 = 2
    F3 = 3
    F4 = 4

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"


class PersonStatus(enum.Enum):
    WAITING = enum.auto()
    ON_ELEVATOR = enum.auto()
    TOOK_STAIRS = enum.auto()
    TOOK_ELEVATOR = enum.auto()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"
    

class BalkingStrategy(enum.Enum):
    NO_BALKING = enum.auto()
    DEFAULT_BALKING = enum.auto()


class ElevatorStatus(enum.Enum):
    WAITING = enum.auto()
    LOADING = enum.auto()
    TRAVELLING = enum.auto()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"


class Person:
    __next_id: int = 0
    def __init__(
        self,
        *,
        destination: Floor = Floor.GROUND,
        arrival_time: float = -1.0,
        id: int | None= None,
    ):
        self.destination = destination
        self.arrival_time = arrival_time
        self.status: PersonStatus = PersonStatus.WAITING
        if id is not None:
            self.id = id
        else:
            self.id = self.__class__.__next_id
            self.__class__.__next_id += 1

        self.elevator_load_time: float = -1.0
        self.elevator_unload_time: float = -1.0
        self.take_stairs_time: float = -1.0

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            + f"(id={self.id!r}, "
            + f"destination={self.destination!r}, "
            + f"arrival_time={self.arrival_time!r}, "
            + f"status={self.status!r}"
            + f")"
        )
    
    def left_queue_time(self) -> float:
        if self.elevator_load_time > 0.0:
            return self.elevator_load_time
        else:
            return self.take_stairs_time

    def balk(self, random: random.Random) -> bool:
        if self.destination == Floor.F2:
            return random.random() < 0.5
        elif self.destination == Floor.F3:
            return random.random() < 0.33
        elif self.destination == Floor.F4:
            return random.random() < 0.10
        else:
            raise ValueError(f"Invalid destination {self.destination!r}")
        pass


travel_time_map = {
    (Floor.GROUND, Floor.GROUND): 0.0,
    (Floor.GROUND, Floor.F2): 1.0,
    (Floor.GROUND, Floor.F3): 1.5,
    (Floor.GROUND, Floor.F4): 1.75,
    (Floor.F2, Floor.GROUND): 1.00,
    (Floor.F2, Floor.F2): 0.00,
    (Floor.F2, Floor.F3): 0.50,
    (Floor.F2, Floor.F4): 0.75,
    (Floor.F3, Floor.GROUND): 1.50,
    (Floor.F3, Floor.F2): 0.50,
    (Floor.F3, Floor.F3): 0.00,
    (Floor.F3, Floor.F4): 0.50,
    (Floor.F4, Floor.GROUND): 1.75,
    (Floor.F4, Floor.F2): 0.50,
    (Floor.F4, Floor.F3): 0.25,
    (Floor.F4, Floor.F4): 0.00,
}


class Elevator:
    def __init__(
        self,
        *,
        capacity: int = 12,
        unload_time: float = 0.5,
        load_time: float = 0.5,
    ) -> None:
        self.capacity = capacity
        self.unload_time = unload_time
        self.load_time = load_time

        self.status = ElevatorStatus.WAITING
        self.current_floor: Floor = Floor.GROUND

        self.occupants: list[Person] = []
        self.occupant_destinations: list[Floor] = []

    def load(self, waiting: deque[Person], start_time: float) -> float:
        logging.debug(f"[load()] {len(waiting)=} {start_time=}")
        self.status = ElevatorStatus.LOADING
        remaining_capacity = self.capacity - len(self.occupants)

        stop_loading_time = start_time + self.load_time
        for _ in range(remaining_capacity):
            if len(waiting) == 0:
                logging.debug(f"[load()] No one left in waiting queue")
                break
            peek_person = waiting[0]
            if peek_person.arrival_time > stop_loading_time:
                # This person (and all subsequent people in the queue)
                # Arrived after the doors closed.
                # 
                # Stop loading people onto the elevator
                break
            else:
                # This person arrived before the doors closed, and there is
                # room for them in the elevator.
                #
                # Move them from the arrival queue to the elevator passengers
                person_loading = peek_person
                waiting.popleft()
                person_loading.status = PersonStatus.ON_ELEVATOR

                # The person's load time is the loading start time, if they were already waiting
                # If they showed up during the loading, their laod time is 
                person_loading.elevator_load_time = max(person_loading.arrival_time, start_time)
                logging.debug(f"[load()] Loaded {person_loading}")
                self.occupants.append(person_loading)
        
        # Destination(s) will be all of the floor(s) of all occupants
        # in ascending order, determined at passenger load time.
        # This won't work in more general loading cases, but will work
        # in the scenario described in the problem statement.
        # 
        # See fuller discussion about travel strategy in report document.
        self.occupant_destinations = sorted({
            person.destination
            for person
            in self.occupants
        })
        logging.debug(f"[load()] Elevator destination(s): {self.occupant_destinations}")
        return stop_loading_time

    def unload(self, start_time: float) -> float:
        # Iterate over the list in reverse so that we can safely .pop(index) without
        # modifying the portion of the list we haven't yet iterated over.
        for index in reversed(range(len(self.occupants))):
            person_unloading = self.occupants[index]
            if person_unloading.destination == self.current_floor:
                person_unloading.status = PersonStatus.TOOK_ELEVATOR
                person_unloading.elevator_unload_time = start_time
                logging.debug(f"[unload()] UNLOADING {person_unloading} on {self.current_floor}")
                self.occupants.pop(index)
        return start_time + self.unload_time

    def travel_to(
        self,
        destination_floor: Floor,
        start_time: float
    ) -> float:
        travel_time = travel_time_map[(self.current_floor, destination_floor)]
        self.current_floor = destination_floor
        return start_time + travel_time

    def travel(self, start_time: float) -> float:
        """Do a "circuit" of travel:
        
        1. start with a loaded elevator at GROUND
        2. Travel to destination floor(s) and unload
        3. Return to GROUND
        """
        logging.debug(f"[travel()] ***** called at {start_time=} *****")

        time = start_time
        while self.occupant_destinations:
            logging.debug(f"[travel()] {time=}")
            logging.debug(f"[travel()] {self.occupant_destinations=}")
            destination_floor = self.occupant_destinations.pop(0)
            time = self.travel_to(destination_floor, start_time=time)
            logging.debug(f"[travel()] Finish travel_to({destination_floor!r}) at {time}")
            time = self.unload(time)
            logging.debug(f"[travel()] Finish unload() at {time}")

        logging.debug(f"[travel()] Done delivering. Returning to GROUND from {self.current_floor} at t={time}")
        time = self.travel_to(Floor.GROUND, start_time=time)
        logging.debug(f"[travel()] ***** DONE with everything at t={time} *****")
        self.status = ElevatorStatus.WAITING
        return time



        # if self.occupant_destinations:
        #     logging.debug(f"[travel()] {self.occupant_destinations=}")
        #     destination_floor = self.occupant_destinations.pop(0)
        #     logging.debug(f"[travel()] {destination_floor=}")
        # else:
        #     destination_floor = Floor.GROUND
        # return self.travel_to(
        #     destination_floor=destination_floor,
        #     start_time=start_time,
        # )

class Simulation:
    def __init__(
        self,
        *,
        seed: int = 0,
        arrival_rate: float = 1 / 6,
        balking_strategy: BalkingStrategy = BalkingStrategy.DEFAULT_BALKING
    ) -> None:
        self.time: float = 0.0
        """Minutes since 8:00:00 A.M."""
        self.random = random.Random(seed)
        self.arrival_rate = arrival_rate
        self.balking_strategy = balking_strategy
        self.elevator = Elevator()
        self.arrival_queue = self.generate_arrival_queue()

        # self.wont_balk: set[Person] = set()
        # """People who have made the decision that they won't ever balk."""

        self.all_people = list(self.arrival_queue)
        logging.debug(f"Created arrival queue. Size={len(self.arrival_queue)}")
        self.main_loop()

    def generate_arrival_queue(self, simulation_stop_time: float = 60.0) -> deque[Person]:
        arrival_time = 0.0
        count = 0
        persons: deque[Person] = deque()
        while arrival_time < simulation_stop_time:
            count += 1
            wait_time = self.random.expovariate(1 / self.arrival_rate)
            arrival_time += wait_time
            if arrival_time > simulation_stop_time:
                break
            persons.append(Person(
                destination=self.random.choice((
                    Floor.F2,
                    Floor.F3,
                    Floor.F4,
                )),
                arrival_time=arrival_time
            ))
        return persons
    
    def main_loop(self):
        """The main loop of the simulation
        
        Continue processing arrivals until (time > 9:00 A.M.) and (queue is empty)"""
        logging.debug(f"Started main loop. {self.time=}")
        while self.arrival_queue:
            logging.debug(f"[main_loop] ---------- New iteration @ t={self.time} ----------")

            # if self.elevator.current_floor == Floor.GROUND and self.elevator.status == ElevatorStatus.WAITING:
            logging.debug(f"[main_loop] at t={self.time}, Elevator at GROUND and WAITING")

            # Figure out if someone is waiting or not
            next_person = self.arrival_queue[0]
            is_someone_waiting = next_person.arrival_time <= self.time

            if not is_someone_waiting:
                # If no one is waiting, the elevator will just sit here until someone arrives
                # so we can just advance the simulation time to the next person's arrival time
                logging.debug(
                    f"[main_loop] Current time is t={self.time}. "
                    + f"Elevator is ready, but next arrival is at t={next_person.arrival_time}. "
                    + f"Advancing simulation time to t={next_person.arrival_time}"
                )
                self.time = next_person.arrival_time
                continue
            else:
                logging.debug(f"[main_loop] There is at least one person waiting at t={self.time}")

            logging.debug(f"[main_loop] Handling balking")
            self.handle_balking()

            logging.debug(f"[main_loop] at t={self.time}, elevator begins loading")
            load_end_time = self.elevator.load(
                waiting=self.arrival_queue,
                start_time=self.time,
            )
            self.time = load_end_time
            logging.debug(f"[main_loop] at t={self.time}, elevator finishes loading")
            logging.debug(f"[main_loop] at t={self.time}, elevator begins travel")
            travel_end_time = self.elevator.travel(self.time)
            self.time = travel_end_time
            logging.debug(f"[main_loop] at t={self.time}, elevator finishes travel")

    def handle_balking(
        self,
    ):
        if self.balking_strategy == BalkingStrategy.NO_BALKING:
            logging.debug(f"[handle_balking()] There's no balking. Returning, making no errors")
            return
        
        people_in_queue = [
            person
            for person
            in self.arrival_queue
            if person.arrival_time <= self.time
        ]
        logging.debug(f"[handle_balking()] There are {len(people_in_queue)} people in queue at t={self.time}")
        if people_in_queue:
            logging.debug(f"[handle_balking()] Earliest arrival: {people_in_queue[0].arrival_time}")
            logging.debug(f"[handle_balking()] Latest arrival:   {people_in_queue[-1].arrival_time}")
        
        first_twelve = people_in_queue[ : 12]
        remainder = people_in_queue[12 : ]

        logging.debug(f"[handle_balking()] {len(first_twelve)=}")
        if first_twelve:
            logging.debug(f"[handle_balking()] Earliest arrival: {first_twelve[0].arrival_time}")
            logging.debug(f"[handle_balking()] Latest arrival:   {first_twelve[-1].arrival_time}")


        logging.debug(f"[handle_balking()] {len(remainder)=}")
        if remainder:
            logging.debug(f"[handle_balking()] Earliest arrival: {remainder[0].arrival_time}")
            logging.debug(f"[handle_balking()] Latest arrival:   {remainder[-1].arrival_time}")
        
        for person in remainder:
            if person.balk(self.random):
                person.status = PersonStatus.TOOK_STAIRS
                person.take_stairs_time = self.time
                self.arrival_queue.remove(person)

    def elevator_people(self) -> list[Person]:
        return [
            person
            for person
            in self.all_people
            if person.status == PersonStatus.TOOK_ELEVATOR
        ]
    
    def stair_people(self) -> list[Person]:
        return [
            person
            for person
            in self.all_people
            if person.status == PersonStatus.TOOK_STAIRS
        ]


if __name__ == "__main__":
    simulation = Simulation(
        seed=1,
    )
    from collections import Counter

    counter = Counter()

    for person in simulation.all_people:
        # print(f"{person.id} {person.destination} {person.arrival_time} {person.elevator_load_time} {person.elevator_unload_time}")
        counter[person.status] += 1
    
    balkers = [
        person
        for person
        in simulation.all_people
        if person.status == PersonStatus.TOOK_STAIRS
    ]


    elevator_riders = [
        person
        for person
        in simulation.all_people
        if person.status == PersonStatus.TOOK_ELEVATOR
    ]

    for person in elevator_riders:
        wait_time = person.elevator_load_time - person.arrival_time
        print(f"{person.id=}  {person.destination!r}  {wait_time}")

    print(counter)