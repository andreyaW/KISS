''' simulate an aux ship with different sensor configurations to determine how many moderate sensors are needed to match
    the accuracy of a few good sensors '''

from shipClass.Ship import Ship
from shipClass.SensedShip import SensedShip

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm  # <-- progress bar library

# ---- Main function ----

def main():

    simulation_hours = 1440     # simulate for 1440 hours (60 days)
    num_sims = 100              # number of simulations to average accuracy over

    # run the ship with good sensor configuration (baseline)
    num_sensors = 1
    quality = 'good'
    ship = Ship('RepairableShip', 'auxiliary_ship_data.xlsx', repairable=True, np_rng_num= 15)
    sensed_ship = SensedShip(ship, [[(num_sensors, quality) for _ in system.comps] for system in ship.systems.values()])
    sensed_ship.attach_sensors()

    good_accuracy = np.zeros(num_sims)  # store accuracies for averaging
    print("\nRunning baseline (good sensors)...")
    for i in tqdm(range(num_sims), desc="Baseline runs", ncols=80):  # <-- added progress bar here
        sensed_ship.simulate(1440)  # simulate for 1440 hours
        # sensed_ship.plotHistory()    
        good_accuracy[i] = sensed_ship.checkSensingAccuracy()
        sensed_ship.reset()  # reset for next run
    good_accuracy = np.mean(good_accuracy)
    print(f"\nBaseline: {good_accuracy:.2f}% accuracy with {num_sensors} '{quality}' sensors per component over 1440 hours.")

    # initial moderate sensor configuration
    num_sensors = 3
    max_sensors = 25            # max number of moderate sensors to try
    quality = 'moderate'
    comparison_limit = 1        # percent accuracy difference to stop simulations

    # X,Y FOR PLOTTING
    moderate_sensor_counts = [0]
    moderate_accuracies = [0]  # let index 0 be dummy for starting the simulation loop

    print("\nRunning moderate sensor comparisons...\n")

    # iteratively add sensors until similar accuracy is achieved with moderate sensors
    while abs(moderate_accuracies[-1] - good_accuracy) > comparison_limit:  # within 1% of good accuracy

        # simulate current configuration n times and average accuracy
        # print(f"Testing {num_sensors} '{quality}' sensors per component...")
        # create a new ship
        ship = Ship('RepairableShip', 'auxiliary_ship_data.xlsx', repairable=True, np_rng_num= 15)
        
        # attach sensors
        sensors = [[(num_sensors, quality) for _ in system.comps]
                for system in ship.systems.values()]
        sensed_ship = SensedShip(ship, sensors)
        sensed_ship.attach_sensors()

        accuracy = np.zeros(num_sims)
        for i in tqdm(range(num_sims), desc=f"{num_sensors} sensors per comp", ncols=80):  # <-- added progress bar here too
            # simulate the current configuration
            sensed_ship.simulate(simulation_hours)
            accuracy[i] = sensed_ship.checkSensingAccuracy()
            sensed_ship.reset()  # reset for next run

        # record results for plotting  
        print(f"  {num_sensors} '{quality}' sensors per component: {np.mean(accuracy):.2f}% accuracy over {simulation_hours} hours (averaged over {num_sims} runs).")
        accuracy = np.mean(accuracy)
        moderate_sensor_counts.append(num_sensors)
        moderate_accuracies.append(accuracy)

        # increment sensors
        num_sensors += 1
        if num_sensors > max_sensors:   # max 25 sensors per component
            break

    if num_sensors == max_sensors:
        print(f"\nMax sensors reached; {moderate_accuracies[-1]:.2f}% accuracy with {num_sensors-2} '{quality}' sensors per component over {simulation_hours} hours.")
    else:
        print(f"\nAchieved {moderate_accuracies[-1]:.2f}% accuracy with {num_sensors-2} '{quality}' sensors per component over {simulation_hours} hours.")

    # plot accuracy vs number of sensors
    plt.figure()
    plt.plot(moderate_sensor_counts[1:], [acc for acc in moderate_accuracies[1:]], marker='o', label=f"'{quality}' sensors")
    plt.axhline(y=good_accuracy, color='r', linestyle='--', label=f"'Good' sensors baseline ({good_accuracy:.2f}%)")
    plt.xlabel('Number of Sensors per Component')
    plt.ylabel('Sensing Accuracy (%)')
    plt.title('Sensing Accuracy vs Number of Sensors')
    plt.legend()
    plt.grid()
    plt.show()

    # Save the figure
    plt.savefig(f'moderate_sensing_accuracy_vs_number_of_sensors.png', bbox_inches='tight')

if __name__ == "__main__":
    main()
