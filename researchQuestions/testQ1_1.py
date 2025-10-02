import xlsxwriter
from shipClass.Ship import Ship
from shipClass.SensedShip import SensedShip
from utils.helperFunctions import create_multi_simulation_table
from simCalcFunctions import *

import numpy as np
import multiprocessing as mp
from tqdm import tqdm
import time
import numpy.random as npr
npr.seed(1)  # for reproducibility


# ---- Worker function ----
def run_simulation_worker(batch_indices, num_sensors, quality, worker_ship, result_queue):
    """
    Each worker runs a batch of simulations using its dedicated Ship instance.
    """
    for j in batch_indices:
        # attach sensors
        sensors = [[(num_sensors, quality) for comps in system.comps]
                   for system in worker_ship.systems.values()]
        sensed_ship = SensedShip(worker_ship, sensors)
        sensed_ship.attach_sensors()

        # simulate for 720 hours
        sensed_ship.simulate(720)

        # collect metrics
        truth_history = sensed_ship.ship.history
        sensed_history = sensed_ship.sensedHistory
        correct, incorrect = countRightAndWrongReadings(truth_history, sensed_history)
        false_fails, false_alarms = countFalseNegatives(truth_history, sensed_history)
        # unsensed_fails, unsensed_alarms =

        # reset ship for next simulation
        sensed_ship.reset()

        # send results back to main process
        result_queue.put((num_sensors, quality, j, correct, incorrect,
                          false_fails, false_alarms))

# ---- Main function ----
def main():
    num_simulations = 10
    num_cores = 6  # adjust as needed
    simulation_parameters =[(1, 'bad'),        # 1 bad quality sensor per component
                            (1, 'moderate'),   # 1 moderate quality sensor per component
                            (1, 'good'),       # 1 good quality sensor per component
                            (3, 'bad'),        # 3 bad quality sensors per component
                            (3, 'moderate'),   # 3 moderate quality sensors per component
                            (3, 'good'),       # 3 good quality sensors per component
                            (7, 'bad'),        # 7 bad quality sensors per component
                            (7, 'moderate'),   # 7 moderate quality sensors per component
                            (7, 'good'),       # 7 good quality sensors per component
                            (11, 'bad'),       # 11 bad quality sensors per component
                            (11, 'moderate'),  # 11 moderate quality sensors per component
                            (11, 'good')]      # 11 good quality sensors per component

    # pre-allocate result arrays
    count_correct = np.zeros((len(simulation_parameters), num_simulations))              # truth == sensed
    count_incorrect = np.zeros((len(simulation_parameters), num_simulations))            # truth != sensed
    count_false_failures = np.zeros((len(simulation_parameters), num_simulations))      # truth == 0, sensed != 0
    count_false_alarms = np.zeros((len(simulation_parameters), num_simulations))        # truth ==1, sensed != 1
    count_unsensed_failures = np.zeros((len(simulation_parameters), num_simulations))    # truth != 0, sensed == 0
    count_unsensed_alarms = np.zeros((len(simulation_parameters), num_simulations))      # truth != 1, sensed == 1 

    # pre-create one master ship per worker
    print("Creating master ships for each worker...")
    ships_per_worker = [Ship('RepairableShip', 'auxiliary_ship_data.xlsx', repairable=True)
                        for _ in range(num_cores)]

    manager = mp.Manager()
    result_queue = manager.Queue()

    processes = []
    total_sims = len(simulation_parameters) * num_simulations
    pbar = tqdm(total=total_sims, desc="Running simulations")

    # dispatch tasks: each simulation parameter is split into batches for workers
    for i, (num_sensors, quality) in enumerate(simulation_parameters):
        # split simulations into batches for workers
        batch_size = (num_simulations + num_cores - 1) // num_cores
        for worker_idx in range(num_cores):
            start = worker_idx * batch_size
            end = min(start + batch_size, num_simulations)
            if start >= end:
                continue  # skip empty batch
            batch_indices = list(range(start, end))
            worker_ship = ships_per_worker[worker_idx]
            p = mp.Process(target=run_simulation_worker,
                           args=(batch_indices, num_sensors, quality, worker_ship, result_queue))
            p.start()
            processes.append(p)

    # collect results as they come
    collected = 0
    while collected < total_sims:
        (num_sensors, quality, j, correct, incorrect,
         missed_failures, missed_alarms, unsensed_fails, unsensed_alarms) = result_queue.get()
        i = simulation_parameters.index((num_sensors, quality))
        count_correct[i][j] = correct
        count_incorrect[i][j] = incorrect
        count_false_failures[i][j] = missed_failures
        count_false_alarms[i][j] = missed_alarms
        count_unsensed_failures[i][j] = unsensed_fails
        count_unsensed_alarms[i][j] = unsensed_alarms
        collected += 1
        pbar.update(1)

    pbar.close()

    # join all worker processes
    for p in processes:
        p.join()

    # summarize results
    headers = ["Simulation Parameters", "Correct Readings", "Incorrect Readings", 
               "Missed Failures", "Missed Alarms", "Unsensed Failures", "Unsensed Alarms"]
    rows = []
    for i, param in enumerate(simulation_parameters):
        rows.append([
            param,
            count_correct[i].mean(),
            count_incorrect[i].mean(),
            count_missed_failures[i].mean(),
            count_missed_alarms[i].mean(),
            count_unsensed_failures[i].mean(),
            count_unsensed_alarms[i].mean()
        ])
    print(create_multi_simulation_table(headers, rows))

    # -------- Export to Excel --------
    output_file = "test1_1_simulation_results.xlsx"
    workbook = xlsxwriter.Workbook(output_file)
    worksheet = workbook.add_worksheet("Summary")

    # write headers
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    # write rows
    for row_idx, row_data in enumerate(rows, start=1):
        for col_idx, value in enumerate(row_data):
            worksheet.write(row_idx, col_idx, value)

    workbook.close()
    print(f"Results exported to {output_file}")

if __name__ == "__main__":
    import cProfile
    import pstats
    with cProfile.Profile() as pr:
        main()
    stats = pstats.Stats(pr)
    stats.sort_stats("cumtime").print_stats(30)
