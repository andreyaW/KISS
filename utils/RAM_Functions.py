import numpy as np
import matplotlib.pyplot as plt

from tabulate import tabulate

# ---------------- BASIC RELIABILITY FUNCTIONS----------------- #

def drawRelCurve(failure_times):
    """Draws the reliability curve based on the failure times of simulated components"""
    # Calculate the reliability function R(t)
    t = np.linspace(0, np.max(failure_times), len(failure_times))  # Time points for the reliability curve
    # R_t = np.array([np.mean(failure_times > ti) for ti in t])
    # R_t = np.array([np.sum(failure_times > ti) / len(failure_times) for ti in t])  # Reliability function

    failure_times_sorted = np.sort(failure_times)
    R_t = []
    for time in t:
        R_t.append(np.sum(failure_times_sorted > time) / len(failure_times_sorted))

    # Plot the reliability curve
    plt.plot(t, R_t, label='Reliability Function R(t)')
    plt.xlabel('Time')
    plt.ylabel('Reliability')
    plt.title('Reliability Curve')
    plt.grid()
    plt.legend()
    plt.show()


def calculate_availability(history):
    uptime = sum(1 for status in history if status == 2)
    downtime = sum(1 for status in history if status == 0)
        # total_time = len(history)
    availability = uptime / (uptime+downtime)
    return availability


# ---------------- UNMANNNED RELIABILITY FUNCTIONS----------------- #
# def calculate_sensor_reliability(true_histories, sensed_histories):
#     """ Calculate relevant discrepancies between true and sensed histories """
#     headers = ["Percent Major Fails Missed", 
#                "Percent Incipent Fails Missed"]

#     num_ships = len(true_histories)
#     percent_incipent_fails_missed = [0]*num_ships
#     percent_major_fails_missed = [0]*num_ships

#     for i in range(len(true_histories)):
#         true_history = true_histories[i]
#         sensed_history = sensed_histories[i]

#         # determine the percent of major failures missed    
#         num_major_fails = sum(1 for status in true_history if status == 0)
#         sensed_major_fails = sum(1 for t_status, s_status in zip(true_history, sensed_history) if t_status == 0 and s_status == 0)
#         percent_major_fails_missed[i] = (num_major_fails - sensed_major_fails) / num_major_fails if num_major_fails > 0 else 0

#         # determine the percent of incipent failures missed
#         num_incipent_fails = sum(1 for status in true_history if status == 1)
#         sensed_incipent_fails = sum(1 for t_status, s_status in zip(true_history, sensed_history) if t_status == 1 and s_status == 1)
#         percent_incipent_fails_missed[i] = (num_incipent_fails - sensed_incipent_fails) / num_incipent_fails if num_incipent_fails > 0 else 0

#     table = tabulate([percent_major_fails_missed, percent_incipent_fails_missed], headers=headers, tablefmt="grid")
#     return table

def calculate_sensor_reliability(true_histories, sensed_histories):
    """ Calculate relevant discrepancies between true and sensed histories """
    headers = ["Ship ID", 
               "Number of Major Fails Missed", 
               "Number of Incipent Fails Missed"]

    num_ships = len(true_histories)

    for i in range(num_ships):
        true_history = true_histories[i]
        sensed_history = sensed_histories[i]

        #1. number of unexpected major failures (sensed as healthy or incipient but actually failed)
        num_major_fails = sum(1 for status in true_history if status == 0)
        sensed_major_fails = sum(1 for t_status, s_status in zip(true_history, sensed_history) 
                                 if t_status == 0 and s_status == 0)
        major_fails_missed = (num_major_fails - sensed_major_fails)

        # 2. the numbe of incipent failures missed
        num_incipent_fails = sum(1 for status in true_history if status == 1)
        sensed_incipent_fails = sum(1 for t_status, s_status in zip(true_history, sensed_history) 
                                    if t_status == 1 and s_status == 1)
        incipent_fails_missed = num_incipent_fails - sensed_incipent_fails
        
        # build the row directly
        row = [
            i + 1,  # Ship ID
            major_fails_missed,
            incipent_fails_missed
        ]

    return row


def create_multi_simulation_table(headers, rows):
    """ Create a table summarizing the results of multiple simulations """
    return tabulate(rows, headers=headers, tablefmt="grid")



# def periodic_Maintenance(PM_interval: float, PM_period: float, current_time_step: int, system):

#     # skip maintenance if not time for periodic maintenance
#     if np.mod(current_time_step, PM_interval) != 0:
#         pass    

#     # if the simulation is at the periodic maintenance interval, do maintenance on the system
#     else: 

#         for comp in system.comps: 
#             pass
#             # check if the comp is functional
            
#             # complete maintenance on comp if it is not functional

            
#         print("add system maintenance functionality here")
    
#     return system
