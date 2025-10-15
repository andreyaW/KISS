import numpy as np
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D  # needed for older matplotlib versions
from shipClass.Ship import Ship
from shipClass.SensedShip import SensedShip
from shipClass.Sensor_basic import Sensor
from tqdm import tqdm  # <-- progress bar library


def main():
    ''' Compare the accuracy of a few moderate sensors to good sensors '''

    simulation_hours = 1440     # simulate for 1440 hours (60 days)
    num_sims = 100              # number of simulations to average accuracy over

    baseline_accuracy = 98.0    # baseline accuracy for good sensors 

    # initial moderate sensor configuration
    num_sensors = 3
    max_sensors = 25                                   # max number of moderate sensors to try
    quality = 'moderate'
    comparison_limit = 1        # percent accuracy difference to stop simulations

    # ---- X, Y, Z FOR PLOTTING ----
    # X: sensor probability of correct detection
    probs_correct = np.linspace(start=0.6, stop=0.85, num=20) # (moderate sensor prob. correct detection ranges 60% to 85% accuracy)

    # Y: overall sensed accuracy (nearly constant, small variation)
    # Y_vals = baseline_accuracy + 0.3 * np.sin(np.linspace(0, 2*np.pi, len(probs_correct)))  # small wave around 98%
    Y_vals = np.zeros(len(probs_correct))  # initialize Y values
    Z_vals = np.zeros(len(probs_correct))  # Z: number of sensors per component (inversely related to X)

    for i, prob in enumerate(probs_correct):

        # create a new ship
        test_ship = Ship('RepairableShip', 'auxiliary_ship_data.xlsx', repairable=True, np_rng_num= 15)

        # iteratively add sensors until similar accuracy is achieved with moderate sensors
        while abs(Y_vals[-1] - baseline_accuracy) > comparison_limit:  # within 1% of good accuracy

            # attach sensors
            sensors = [[(num_sensors, quality) for _ in system.comps]
                    for system in test_ship.systems.values()]
            sensed_ship = SensedShip(test_ship, sensors)
            sensed_ship.attach_sensors()

            # Set all sensors to have the current probability of correct detection
            for sensor_set in sensed_ship.sensors:
                for sensor in sensor_set:
                    sensor.setObservationProbs(value=prob)

            # simulate current configuration n times and average accuracy
            accuracy = np.zeros(num_sims)
            for i in tqdm(range(num_sims), desc=f"{num_sensors} sensors per comp", ncols=80):  # <-- added progress bar here too
                # simulate the current configuration
                sensed_ship.simulate(simulation_hours)
                accuracy[i] = sensed_ship.checkSensingAccuracy()
                sensed_ship.reset()  # reset for next run

            # record results for plotting  
            Y_vals[i] = np.mean(accuracy)
            # High X (more accurate sensors) → fewer sensors needed
            Z_vals = num_sensors           # Z: number of sensors per component (inversely related to X)
            
            # increment sensors
            num_sensors += 1
            if num_sensors > max_sensors:   # max 25 sensors per component
                break
       
    # Create 2D grid for surface plotting
    X, Y = np.meshgrid(probs_correct, Y_vals)   #(~constant along Y)

    # ---- 3D Surface Plot ----
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    surf = ax.plot_surface(X, Y, Z_vals, cmap='viridis', edgecolor='none', alpha=0.9)

    # Labels and title
    ax.set_xlabel('Sensor Probability of Correct Detection', labelpad=10)
    ax.set_ylabel('Overall Sensed State Accuracy (%)', labelpad=10)
    ax.set_zlabel('Number of Sensors per Component', labelpad=10)
    ax.set_title('Sensor Detection Accuracy vs Overall Accuracy vs Sensor Count')

    # Adjust view for better perception
    ax.view_init(elev=25, azim=135)

    fig.colorbar(surf, ax=ax, shrink=0.6, aspect=10, label='Sensor Count Value')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()





        # # (baseline) ship with a single good sensor configuration (98% accurate)
        # num_sensors = 1
        # quality = 'good'
        # ship = Ship('RepairableShip', 'auxiliary_ship_data.xlsx', repairable=True, np_rng_num= 15)
        # sensed_ship = SensedShip(ship, [[(num_sensors, quality) for _ in system.comps] for system in ship.systems.values()])
        # sensed_ship.attach_sensors()

        # good_accuracy = np.zeros(num_sims)  # array to store accuracies for averaging
        # print("\nRunning baseline (good sensors)...")
        # for i in tqdm(range(num_sims), desc="Baseline runs", ncols=80):  # <-- added progress bar here
        #     sensed_ship.simulate(1440)      # simulate for 1440 hours
        #     good_accuracy[i] = sensed_ship.checkSensingAccuracy()
        #     sensed_ship.reset()             # reset for next run
        # baseline_accuracy = np.mean(good_accuracy)
        # print(f"\nBaseline: {baseline_accuracy:.2f}% accuracy with {num_sensors} '{quality}' sensors per component over 1440 hours.")




    # print("\nRunning moderate sensor comparisons...\n")

    # for i, prob in enumerate(prob_correct):
    #     # iteratively add sensors until similar accuracy is achieved with moderate sensors
    #     while abs(moderate_accuracies[-1] - good_accuracy) > comparison_limit:  # within 1% of good accuracy

    #         # print(f"Testing {num_sensors} '{quality}' sensors per component...")

    #         # create a new ship
    #         ship = Ship('RepairableShip', 'auxiliary_ship_data.xlsx', repairable=True, np_rng_num= 15)
            
    #         # attach sensors
    #         sensors = [[(num_sensors, quality) for _ in system.comps]
    #                 for system in ship.systems.values()]
    #         sensors = [sensor.setObservationProbs(value=prob_correct) for sensor_set in sensors for sensor in sensor_set]
    #         sensed_ship = SensedShip(ship, sensors)
    #         sensed_ship.attach_sensors()

    #         # simulate current configuration n times and average accuracy
    #         accuracy = np.zeros(num_sims)
    #         for i in tqdm(range(num_sims), desc=f"{num_sensors} sensors per comp", ncols=80):  # <-- added progress bar here too
    #             # simulate the current configuration
    #             sensed_ship.simulate(simulation_hours)
    #             accuracy[i] = sensed_ship.checkSensingAccuracy()
    #             sensed_ship.reset()  # reset for next run

    #         # record results for plotting  
    #         print(f"  {num_sensors} '{quality}' sensors per component: {np.mean(accuracy):.2f}% accuracy over {simulation_hours} hours (averaged over {num_sims} runs).")
    #         accuracy = np.mean(accuracy)
    #         moderate_sensor_counts[i] = num_sensors
    #         moderate_accuracies[i] = accuracy

    #         # increment sensors
    #         num_sensors += 1
    #         if num_sensors > max_sensors:   # max 25 sensors per component
    #             break

    #     if num_sensors == max_sensors:
    #         print(f"\nMax sensors reached; {moderate_accuracies[-1]:.2f}% accuracy with {num_sensors-2} '{quality}' sensors per component over {simulation_hours} hours.")
    #     else:
    #         print(f"\nAchieved {moderate_accuracies[-1]:.2f}% accuracy with {num_sensors-2} '{quality}' sensors per component over {simulation_hours} hours.")

            # 2D Line Plot
            # # plot accuracy vs number of sensors
            # plt.figure()
            # plt.plot(moderate_sensor_counts[1:], [acc for acc in moderate_accuracies[1:]], marker='o', label=f"'{quality}' sensors")
            # plt.axhline(y=good_accuracy, color='r', linestyle='--', label=f"'Good' sensors baseline ({good_accuracy:.2f}%)")
            # plt.xlabel('Number of Sensors per Component')
            # plt.ylabel('Sensing Accuracy (%)')
            # plt.title('Sensing Accuracy vs Number of Sensors')
            # plt.legend()
            # plt.grid()
            # plt.show()

            # # Save the figure
            # plt.savefig(f'moderate_sensing_accuracy_vs_number_of_sensors.png', bbox_inches='tight')
