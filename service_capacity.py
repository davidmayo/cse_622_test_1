from simulation import Simulation, BalkingStrategy


if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt

    sims_per_level = 10
    rates = []
    finish_times = []
    rates_to_check = list(np.arange(0.2, 3.5, 0.05))
    for count, arrival_rate in enumerate(rates_to_check, start=1):
        print(f"Testing {arrival_rate=} [#{count} of {len(rates_to_check)}]")
        sim_times = []

        for seed in range(sims_per_level):
            sim = Simulation(
                seed = seed,
                arrival_rate=1 / arrival_rate,
                balking_strategy=BalkingStrategy.NO_BALKING
            )
            last_person = sim.all_people[-1]
            last_person_wait_time = last_person.elevator_load_time - last_person.arrival_time
            sim_times.append(last_person_wait_time)
        rates.append(arrival_rate)
        finish_times.append(sum(sim_times) / len(sim_times))

    fig, ax = plt.subplots()
    ax: plt.Axes
    ax.plot(rates, finish_times)
    ax.scatter(rates, finish_times)
    ax.set_title(f"Waiting time for last person, given arrival rate\n(Average of {sims_per_level:,} sims each)")
    ax.set_xlabel(f"Arrival rate (people/min)")
    ax.set_ylabel(f"Last arriving person wait time")
    ax.set_ylim(0, max(finish_times)*1.05)
    plt.show()