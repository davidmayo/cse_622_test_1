import matplotlib.pyplot as plt
import numpy as np

from simulation import Simulation, BalkingStrategy, Floor


class SimulationEvaluation:
    def __init__(
        self,
        sim: Simulation
    ) -> None:
        self.sim = sim
        pass

    def queue_length_at(self, time: float) -> float:
        people_in_queue = [
            person
            for person
            in self.sim.all_people
            if person.arrival_time <= time and person.left_queue_time() >= time
        ]
        return len(people_in_queue)
    
    def last_elevator_load_time(self) -> float:
        times = [
            person.elevator_load_time
            for person
            in self.sim.elevator_people()
        ]
        return max(times)
    
    def average_elevator_wait_time(self):
        wait_times = [
            person.elevator_load_time - person.arrival_time
            for person
            in self.sim.elevator_people()
        ]
        return sum(wait_times) / len(wait_times)
    
    def count_walkers_to_floor(self, floor: Floor) -> int:
        walkers = [
            person
            for person
            in self.sim.stair_people()
            if person.destination == floor
        ]
        return len(walkers)
    
    def fraction_walkers_to_floor(self, floor: Floor) -> int:
        """Fraction of people going to the floor who ended up walking"""
        count = self.count_walkers_to_floor(floor)
        denominator = len([
            person
            for person
            in self.sim.all_people
            if person.destination == floor
        ])
        return count / denominator
        pass


if __name__ == "__main__":
    # sim = Simulation(
    #     seed = 0,
    #     balking_strategy=BalkingStrategy.DEFAULT_BALKING,
    # )
    # evaluation = SimulationEvaluation(sim)
    # for t in range(0, 75, 15):
    #     print(f"{t=} {evaluation.queue_length_at(t)=}")

    # print(f"{evaluation.last_elevator_load_time()=}")
    # print(f"{evaluation.average_elevator_wait_time()=}")

    # for floor in [Floor.F2, Floor.F3, Floor.F4]:
    #     print(f"evaluation.count_walkers_to_floor({floor!r})={evaluation.count_walkers_to_floor(floor)}")

    SIM_COUNT = 10_000

    sims = [
        Simulation(seed=seed)
        for seed
        in range(SIM_COUNT)
    ]
    evals = [
        SimulationEvaluation(sim)
        for sim
        in sims
    ]




    # line_8_30 = [
    #     eval.queue_length_at(30.0)
    #     for eval
    #     in evals
    # ]

    # line_8_45 = [
    #     eval.queue_length_at(45.0)
    #     for eval
    #     in evals
    # ]

    # line_9_00 = [
    #     eval.queue_length_at(60.0)
    #     for eval
    #     in evals
    # ]

    
    fig, ax = plt.subplots()
    fig.suptitle(f"Result of {SIM_COUNT:,} simulations")

    
    bins = np.arange(10, 21, 1)
    # for ax in [ax1, ax2, ax3]:
    #     ax.set_ylim(0, SIM_COUNT // 2)
    #     ax.set_xticks(bins)
    #     ax.set_xlabel("BIN")
    # ax1.hist(line_8_30, bins=bins, edgecolor="black")
    # ax1.set_title(f"Length of queue at 8:30")

    # ax2.hist(line_8_45, bins=bins, edgecolor="black")
    # ax2.set_title(f"Length of queue at 8:45")

    # ax3.hist(line_9_00, bins=bins, edgecolor="black")
    # ax3.set_title(f"Length of queue at 9:00")
    # plt.show()



    # wait_times = [
    #     eval.average_elevator_wait_time()
    #     for eval
    #     in evals
    # ]

    # f2_walker_count = [
    #     eval.count_walkers_to_floor(Floor.F2)
    #     for eval
    #     in evals
    # ]
    # f3_walker_count = [
    #     eval.count_walkers_to_floor(Floor.F3)
    #     for eval
    #     in evals
    # ]
    # f4_walker_count = [
    #     eval.count_walkers_to_floor(Floor.F4)
    #     for eval
    #     in evals
    # ]

    # f2_walker_fraction = [
    #     eval.fraction_walkers_to_floor(Floor.F2)
    #     for eval
    #     in evals
    # ]
    # f3_walker_fraction = [
    #     eval.fraction_walkers_to_floor(Floor.F3)
    #     for eval
    #     in evals
    # ]
    # f4_walker_fraction = [
    #     eval.fraction_walkers_to_floor(Floor.F4)
    #     for eval
    #     in evals
    # ]
    # ax1: plt.Axes
    # count_bins = np.arange(0, 140, 10)
    # fraction_bins = np.arange(0.0, 1.05, 0.05)
    # ax1.hist(f2_walker_count, edgecolor="black", bins=count_bins)
    # ax1.set_title(f"Total walk to F2")
    # ax2.hist(f3_walker_count, edgecolor="black", bins=count_bins)
    # ax2.set_title(f"Total walk to F3")
    # ax3.hist(f4_walker_count, edgecolor="black", bins=count_bins)
    # ax3.set_title(f"Total walk to F4")
    # for ax in [ax1, ax2, ax3]:
    #     ax: plt.Axes
    #     ax.set_ylim(0, SIM_COUNT * 6 // 10)
    #     ax.set_xlabel(f"Number (binned)")


    # ax4.hist(f2_walker_fraction, edgecolor="black", bins=fraction_bins)
    # ax4.set_title(f"Fraction of F2 who walk")
    # ax5.hist(f3_walker_fraction, edgecolor="black", bins=fraction_bins)
    # ax5.set_title(f"Fraction of F3 who walk")
    # ax6.hist(f4_walker_fraction, edgecolor="black", bins=fraction_bins)
    # ax6.set_title(f"Fraction of F4 who walk")
    # for ax in [ax4, ax5, ax6]:
    #     ax: plt.Axes
    #     ax.set_ylim(0, SIM_COUNT // 2)
    #     ax.set_xlabel(f"Fraction (binned)")
    # # ax1.hist(wait_times, edgecolor="black", bins=bins)
    # # ax1.set_title(f"Wait time distribution (elevator riders)")
    # # for ax in [ax1]:
    # #     # ax.set_ylim(0, SIM_COUNT // 2)
    # #     ax.set_xticks(bins)
    # #     ax.set_xlabel("BIN")

    last_worker_time = [
        eval.last_elevator_load_time()
        for eval
        in evals
    ]

    ax: plt.Axes
    bins = np.arange(70, 95, 1)
    ax.hist(last_worker_time, bins=bins, edgecolor="black")
    ax.set_title(f"Last elevator boarding time\n(t=0 is 8:00 AM; t=60 is 9:00 AM)")

    plt.tight_layout()
    plt.show()