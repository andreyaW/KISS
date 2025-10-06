from shipClass.Ship import Ship
from shipClass.SensedShip import SensedShip
from utils.helperFunctions import create_multi_simulation_table
from simCalcFunctions import plot_confusion_matrix
from tqdm import tqdm
from sklearn.metrics import confusion_matrix

import numpy as np
import pandas as pd
import multiprocessing as mp
import numpy.random as npr
import os

# ---- Worker function ----
def run_simulation_worker(task):
    sim_id, simulation_hours, num_sensors, quality, num_ships = task

    # set random seed for reproducibility
    npr.seed(sim_id)

    # create a fresh ship per worker
    worker_ship = Ship('RepairableShip', 'auxiliary_ship_data.xlsx', repairable=True)
    # worker_ship = Ship('SimpleShip', 'simple_test_ship_data.xlsx', repairable=True)
 
    # attach sensors
    sensors = [[(num_sensors, quality) for _ in system.comps]
               for system in worker_ship.systems.values()]
    sensed_ship = SensedShip(worker_ship, sensors)
    sensed_ship.attach_sensors()

    # simulate
    sensed_ship.simulate(simulation_hours)
    if num_ships <= 3:
        fig = sensed_ship.plotHistory(show_plot=False, save_path=f"shipHistories/sensed_ship_history_({num_sensors}, '{quality}')_{simulation_hours}Hrs_shipID{sim_id+1}.png")  # disable plot saving

    # build confusion matrix
    truth_history = sensed_ship.ship.history
    sensed_history = sensed_ship.sensedHistory
    cm = confusion_matrix(truth_history, sensed_history, labels=[0, 1, 2])

    return (num_sensors, quality, sim_id, cm)


# ---- Main function ----
def main():
    simulation_parameters = [
        (1, 'bad'), (1, 'moderate'), (1, 'good'),   # 1 sensor per component
        (3, 'bad'), (3, 'moderate'), (3, 'good'),   # 3 sensors per component
        (5, 'bad'), (5, 'moderate'), (5, 'good'),   # 5 sensors per component
        (7, 'bad'), (7, 'moderate'), (7, 'good'),   # 7 sensors per component
        (11, 'bad'), (11, 'moderate'), (11, 'good') # 11 sensors per component
    ]

    num_simulations = 3     # runs per parameter set
    simulation_hours = 720  # hours per run
    num_cores = 4           # max number of workers
    
    # create a folder for confusion matrices output
    new_folder = f"confusionMatrices/{num_simulations}ships"
    os.makedirs(new_folder, exist_ok=True)

    # map param to index for storage
    param_to_idx = {param: idx for idx, param in enumerate(simulation_parameters)}

    # storage for results
    confusion_matrices = np.zeros((len(simulation_parameters), num_simulations, 3, 3))

    # build all tasks
    tasks = []
    for (num_sensors, quality) in simulation_parameters:
        for sim_id in range(num_simulations):
            tasks.append((sim_id, simulation_hours, num_sensors, quality, num_simulations))

    total_sims = len(tasks)

    # run pool of workers
    with mp.Pool(processes=num_cores) as pool:
        for num_sensors, quality, sim_id, cm in tqdm(
            pool.imap_unordered(run_simulation_worker, tasks),
            total=total_sims,
            desc="Running simulations"
        ):
            i = param_to_idx[(num_sensors, quality)]
            confusion_matrices[i, sim_id] = cm

    # summarize results
    headers = [
        "Simulation Parameters", "Correct Readings", "Incorrect Readings",
        "Truth Fail, Sensed Fail", "Truth Fail, Sensed Alarm", "Truth Fail, Sensed Working",
        "Truth Alarm, Sensed Fail", "Truth Alarm, Sensed Alarm", "Truth Alarm, Sensed Working",
        "Truth Working, Sensed Fail", "Truth Working, Sensed Alarm", "Truth Working, Sensed Working"
    ]
    rows = []

    for i, param in enumerate(simulation_parameters):
        # average confusion matrix over all runs and save plot
        cm_mean = confusion_matrices[i].mean(axis=0)

        print(f"Saving Confusion Matrix for {param}:")
        plot_confusion_matrix(cm_mean, param, num_simulations, simulation_hours)

        # unpack cm matrix for excel export        
        c00, c01, c02 = cm_mean[0]
        c10, c11, c12 = cm_mean[1]
        c20, c21, c22 = cm_mean[2]

        rows.append([
            param,
            c00 + c11 + c22,                    # correct
            c01 + c02 + c10 + c12 + c20 + c21,  # incorrect
            c00, c01, c02,
            c10, c11, c12,
            c20, c21, c22
        ])

    # export results for each parameter set
    df = pd.DataFrame(rows, columns=headers)
    df.to_excel("test1_1_simulation_results.xlsx", index=False)


if __name__ == "__main__":
    main()
