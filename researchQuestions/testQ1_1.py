# from shipClass.Ship import Ship
# from shipClass.SensedShip import SensedShip
# from utils.helperFunctions import create_multi_simulation_table
# from simCalcFunctions import *
# from tqdm import tqdm
# from sklearn.metrics import confusion_matrix


# import numpy as np
# import pandas as pd
# import multiprocessing as mp
# import time
# import numpy.random as npr
# npr.seed(1)  # for reproducibility


# # ---- Worker function ----
# def run_simulation_worker(batch_indices, simulation_hours, num_sensors, quality, worker_ship, result_queue):
#     """
#     Each worker runs a batch of simulations using its dedicated Ship instance.
#     """
#     for j in batch_indices:
#         # attach sensors
#         sensors = [[(num_sensors, quality) for comps in system.comps]
#                    for system in worker_ship.systems.values()]
#         sensed_ship = SensedShip(worker_ship, sensors)
#         sensed_ship.attach_sensors()

#         # simulate for 720 hours
#         sensed_ship.simulate(simulation_hours)

#         # collect metrics
#         truth_history = sensed_ship.ship.history
#         sensed_history = sensed_ship.sensedHistory
#         count_correct_fail, count_correct_alarm, count_correct_working = countCorrectReadings(truth_history, sensed_history)
#         true_fail_sensed_alarm, true_fail_sensed_working = countMissedFailures(truth_history, sensed_history)
#         true_alarm_sensed_fail, true_alarm_sensed_working = countMissedAlarms(truth_history, sensed_history)
#         true_working_sensed_fail, true_working_sensed_alarm = countMissedWorkings(truth_history, sensed_history)
        
#         # reset ship for next simulation
#         sensed_ship.reset()

#         # send results back to main process
#         result_queue.put((num_sensors, quality, j, 
#                           count_correct_fail, count_correct_alarm, count_correct_working,
#                           true_fail_sensed_alarm, true_fail_sensed_working,
#                           true_alarm_sensed_fail, true_alarm_sensed_working,
#                           true_working_sensed_fail, true_working_sensed_alarm))

# # ---- Main function ----
# def main():
#     # simulation parameters: (num_sensors, quality)
#     # simulation_parameters = [(3, 'bad'),        # 3 bad quality sensors per component
#     #                         (3, 'moderate'),   # 3 moderate quality sensors per component
#     #                         (3, 'good')]       # 3 good quality sensors per component
    
#     simulation_parameters =[(1, 'bad'),        # 1 bad quality sensor per component
#                             (1, 'moderate'),   # 1 moderate quality sensor per component
#                             (1, 'good'),       # 1 good quality sensor per component
#                             (3, 'bad'),        # 3 bad quality sensors per component
#                             (3, 'moderate'),   # 3 moderate quality sensors per component
#                             (3, 'good'),       # 3 good quality sensors per component
#                             (7, 'bad'),        # 7 bad quality sensors per component
#                             (7, 'moderate'),   # 7 moderate quality sensors per component
#                             (7, 'good'),       # 7 good quality sensors per component
#                             (11, 'bad'),       # 11 bad quality sensors per component
#                             (11, 'moderate'),  # 11 moderate quality sensors per component
#                             (11, 'good')]      # 11 good quality sensors per component
#     num_simulations = 10    # number of times to run each simulation parameter
#     simulation_hours = 720    # number of hours to simulate each ship
#     num_cores = 6             # adjust as needed
    
#     # pre-allocate result arrays
#     count_correct_fails = np.zeros((len(simulation_parameters), num_simulations))    # correctly sensed fail
#     count_correct_alarms = np.zeros((len(simulation_parameters), num_simulations))   # correctly sensed alarm
#     count_correct_workings = np.zeros((len(simulation_parameters), num_simulations))  # correctly sensed working
#     count_true_fail_sensed_alarm_ = np.zeros((len(simulation_parameters), num_simulations))  # sensed alarm, truth fail
#     count_true_fail_sensed_working = np.zeros((len(simulation_parameters), num_simulations)) # sensed working, truth fail
#     count_true_alarm_sensed_fail = np.zeros((len(simulation_parameters), num_simulations))  # sensed fail, truth alarm
#     count_true_alarm_sensed_working = np.zeros((len(simulation_parameters), num_simulations)) # sensed working, truth alarm
#     count_true_working_sensed_fail = np.zeros((len(simulation_parameters), num_simulations))  # sensed fail, truth working
#     count_true_working_sensed_alarm = np.zeros((len(simulation_parameters), num_simulations)) # sensed alarm, truth working
    
#     # pre-create one master ship per worker
#     print("Creating master ships for each worker...")
#     ships_per_worker = [Ship('RepairableShip', 'auxiliary_ship_data.xlsx', repairable=True)
#                         for _ in range(num_cores)]

#     manager = mp.Manager()
#     result_queue = manager.Queue()

#     processes = []
#     total_sims = len(simulation_parameters) * num_simulations
#     pbar = tqdm(total=total_sims, desc="Running simulations")

#     # dispatch tasks: each simulation parameter is split into batches for workers
#     for i, (num_sensors, quality) in enumerate(simulation_parameters):
#         # split simulations into batches for workers
#         batch_size = (num_simulations + num_cores - 1) // num_cores
#         for worker_idx in range(num_cores):
#             start = worker_idx * batch_size
#             end = min(start + batch_size, num_simulations)
#             if start >= end:
#                 continue  # skip empty batch
#             batch_indices = list(range(start, end))
#             print(batch_indices)
#             worker_ship = ships_per_worker[worker_idx]
#                             # p = mp.Process(target=run_simulation_worker,
#                             #                args=(batch_indices, simulation_parameters, simulation_hours,
#                             #                      num_sensors, quality, worker_ship, 
#                             #                      all_truth, all_sensed, result_queue))
#             p = mp.Process(target=run_simulation_worker,
#                            args=(batch_indices, simulation_hours,
#                                  num_sensors, quality, worker_ship, result_queue))
#             p.start()
#             processes.append(p)

#     # collect results as they come
#     collected = 0
#     while collected < total_sims:
#         (num_sensors, quality, j, 
#         correct_fails, correct_alarms, correct_workings, 
#         true_fail_sensed_alarm, true_fail_sensed_working, 
#         true_alarm_sensed_fail, true_alarm_sensed_working, 
#         true_working_sensed_fail, true_working_sensed_alarm) = result_queue.get()
#         i = simulation_parameters.index((num_sensors, quality))
        
#         # Update counts for the results of this simulation
#         count_correct_fails[i,j] = correct_fails
#         count_correct_alarms[i,j] = correct_alarms
#         count_correct_workings[i,j] = correct_workings
#         count_true_fail_sensed_alarm_[i,j] = true_fail_sensed_alarm 
#         count_true_fail_sensed_working[i,j] = true_fail_sensed_working
#         count_true_alarm_sensed_fail[i,j] = true_alarm_sensed_fail
#         count_true_alarm_sensed_working[i,j] = true_alarm_sensed_working
#         count_true_working_sensed_fail[i,j] = true_working_sensed_fail
#         count_true_working_sensed_alarm[i,j] = true_working_sensed_alarm

#         collected += 1
#         pbar.update(1)

#     pbar.close()

#     # join all worker processes
#     for p in processes:
#         p.join()

#     # summarize results
#     headers = ["Simulation Parameters", "Correct Readings", "Incorrect Readings",
#                "Truth Fail, Sensed Fail","Truth Fail, Sensed Alarm", "Truth Fail, Sensed Working",
#                 "Truth Alarm, Sensed Alarm","Truth Alarm, Sensed Fail", "Truth Alarm, Sensed Working",
#                 "Truth Working, Sensed Working","Truth Working, Sensed Fail", "Truth Working, Sensed Alarm"]
#     rows = []
#     for i, param in enumerate(simulation_parameters):

#         # create confusion matrix for this parameter
#         c00 = count_correct_fails[i].mean()              # correctly sensed fail,
#         c01 = count_true_fail_sensed_alarm_[i].mean()    # sensed alarm, truth fail
#         c02 = count_true_fail_sensed_working[i].mean()  # sensed working, truth fail
#         c10 = count_true_alarm_sensed_fail[i].mean()    # sensed fail, truth alarm
#         c11 = count_correct_alarms[i].mean()             # correctly sensed alarm
#         c12 = count_true_alarm_sensed_working[i].mean() # sensed working, truth alarm
#         c20 = count_true_working_sensed_fail[i].mean()   # correctly sensed fail,
#         c21 = count_true_working_sensed_alarm[i].mean()  # sensed alarm, truth normal
#         c22 = count_correct_workings[i].mean()           # sensed working, truth normal
#         print(f"\n Saving Confusion Matrix for Simulation Parameter {param}:")
#         plot_confusion_matrix(f"confusion_matrix_{param}_1000ships.png",
#             c00, c01, c02,
#             c10, c11, c12,
#             c20, c21, c22,
#             labels=["Fail", "Alarm", "Working"])

#         rows.append([
#             param,
#             c00+c11+c22,
#             c01+c02+c10+c12+c20+c21,
#             c00, c01, c02,
#             c10, c11, c12,
#             c20, c21, c22])

#     # print(create_multi_simulation_table(headers, rows))
    
#     # -------- Export to Excel --------
#     df = pd.DataFrame(rows, columns=headers)
#     output_file_path = "test1_1_simulation_results.xlsx"
#     df.to_excel(output_file_path, index=False)

# if __name__ == "__main__":
#     # import cProfile
#     # import pstats
#     # with cProfile.Profile() as pr:
#     main()
#     # stats = pstats.Stats(pr)
#     # stats.sort_stats("cumtime").print_stats(30)


from shipClass.Ship import Ship
from shipClass.SensedShip import SensedShip
from utils.helperFunctions import create_multi_simulation_table
from simCalcFunctions import *
from tqdm import tqdm
from sklearn.metrics import confusion_matrix

import numpy as np
import pandas as pd
import multiprocessing as mp
import numpy.random as npr
npr.seed(1)  # reproducibility


# ---- Worker function ----
def run_simulation_worker(batch_indices, simulation_hours, num_sensors, quality, worker_ship, result_queue):
    """
    Each worker runs a batch of simulations and returns the 3x3 confusion matrix per run.
    """
    for j in batch_indices:
        # attach sensors
        sensors = [[(num_sensors, quality) for _ in system.comps]
                   for system in worker_ship.systems.values()]
        sensed_ship = SensedShip(worker_ship, sensors)
        sensed_ship.attach_sensors()

        # simulate for N hours
        sensed_ship.simulate(simulation_hours)

        # vectorized confusion matrix
        truth_history = sensed_ship.ship.history
        sensed_history = sensed_ship.sensedHistory
        cm = confusion_matrix(truth_history, sensed_history, labels=[0, 1, 2])  # shape (3,3)

        # reset for next sim
        sensed_ship.reset()

        # return result
        result_queue.put((num_sensors, quality, j, cm))


# ---- Main function ----
def main():
    simulation_parameters = [
        (1, 'bad'), (1, 'moderate'), (1, 'good'),
        (3, 'bad'), (3, 'moderate'), (3, 'good'),
        (7, 'bad'), (7, 'moderate'), (7, 'good'),
        (11, 'bad'), (11, 'moderate'), (11, 'good')
    ]

    num_simulations = 100    # number of times to run each parameter set
    simulation_hours = 720  # simulation length in hours
    num_cores = 4           # adjust as needed

    # dictionary for quick lookup
    param_to_idx = {param: idx for idx, param in enumerate(simulation_parameters)}

    # pre-allocate confusion matrix storage
    confusion_matrices = np.zeros((len(simulation_parameters), num_simulations, 3, 3))

    # one master ship per worker
    print("Creating master ships for each worker...")
    ships_per_worker = [Ship('RepairableShip', 'auxiliary_ship_data.xlsx', repairable=True)
                        for _ in range(num_cores)]

    manager = mp.Manager()
    result_queue = manager.Queue()
    processes = []
    total_sims = len(simulation_parameters) * num_simulations
    pbar = tqdm(total=total_sims, desc="Running simulations")

    # dispatch tasks
    for i, (num_sensors, quality) in enumerate(simulation_parameters):
        batch_size = (num_simulations + num_cores - 1) // num_cores
        for worker_idx in range(num_cores):
            start = worker_idx * batch_size
            end = min(start + batch_size, num_simulations)
            if start >= end:
                continue
            batch_indices = list(range(start, end))
            worker_ship = ships_per_worker[worker_idx]
            p = mp.Process(
                target=run_simulation_worker,
                args=(batch_indices, simulation_hours, num_sensors, quality, worker_ship, result_queue)
            )
            p.start()
            processes.append(p)

    # collect results
    collected = 0
    while collected < total_sims:
        (num_sensors, quality, j, cm) = result_queue.get()
        i = param_to_idx[(num_sensors, quality)]
        confusion_matrices[i, j] = cm
        collected += 1
        pbar.update(1)

    pbar.close()

    # join workers
    for p in processes:
        p.join()

    # summarize results
    headers = [
        "Simulation Parameters", "Correct Readings", "Incorrect Readings",
        "Truth Fail, Sensed Fail", "Truth Fail, Sensed Alarm", "Truth Fail, Sensed Working",
        "Truth Alarm, Sensed Fail", "Truth Alarm, Sensed Alarm", "Truth Alarm, Sensed Working",
        "Truth Working, Sensed Fail", "Truth Working, Sensed Alarm", "Truth Working, Sensed Working"
    ]
    rows = []

    for i, param in enumerate(simulation_parameters):
        cm_mean = confusion_matrices[i].mean(axis=0)  # (3,3) average confusion matrix

        # unpack cells
        c00, c01, c02 = cm_mean[0]
        c10, c11, c12 = cm_mean[1]
        c20, c21, c22 = cm_mean[2]

        print(f"Saving Confusion Matrix for {param}:")
        plot_confusion_matrix(
            f"confusionMatrices/confusion_matrix_{param}_{num_simulations}ships_{simulation_hours}Hrs.png",
            c00, c01, c02,
            c10, c11, c12,
            c20, c21, c22,
            labels=["Fail", "Alarm", "Working"]
        )

        rows.append([
            param,
            c00 + c11 + c22,             # correct
            c01 + c02 + c10 + c12 + c20 + c21,  # incorrect
            c00, c01, c02,
            c10, c11, c12,
            c20, c21, c22
        ])

    # export results to Excel
    df = pd.DataFrame(rows, columns=headers)
    df.to_excel("test1_1_simulation_results.xlsx", index=False)


if __name__ == "__main__":
    main()
