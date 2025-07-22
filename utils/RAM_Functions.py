import numpy as np
import matplotlib.pyplot as plt

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


def periodic_Maintenance(PM_interval: float, PM_period: float, current_time_step: int, system):

    # skip maintenance if not time for periodic maintenance
    if np.mod(current_time_step, PM_interval) != 0:
        pass    

    # if the simulation is at the periodic maintenance interval, do maintenance on the system
    else: 

        for comp in system.comps: 
            pass
            # check if the comp is functional
            
            # complete maintenance on comp if it is not functional

            
        print("add system maintenance functionality here")
    
    return system
