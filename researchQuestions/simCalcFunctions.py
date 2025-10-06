
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# --- Function to count correct readings by category ---
def countCorrectReadings(truth_history, sensed_history):
    """
    Determine all correct sensor readings by category
    """
    # correct readings by category
    correct_fail = 0
    correct_alarm = 0
    correct_working = 0

    for sensedState, trueState in zip(sensed_history, truth_history):
        if sensedState == trueState:
            if sensedState == 0:
                correct_fail += 1
            elif sensedState == 1:
                correct_alarm += 1
            elif sensedState == 2:
                correct_working += 1

    return correct_fail, correct_alarm, correct_working

# --- Function to count missed failures, alarms, and workings ---

def countMissedFailures(truth_history, sensed_history):
    """
    Determine all missed failures
    """
    true_fail_sensed_alarm = 0
    true_fail_sensed_working = 0

    for sensedState, trueState in zip(sensed_history, truth_history):
        if trueState == 0:  # true fail
            if sensedState == 1:  # sensed alarm
                true_fail_sensed_alarm += 1
            elif sensedState == 2:  # sensed working
                true_fail_sensed_working += 1

    return true_fail_sensed_alarm, true_fail_sensed_working

def countMissedAlarms(truth_history, sensed_history):
    """
    Determine all missed alarms
    """
    true_alarm_sensed_fail = 0
    true_alarm_sensed_working = 0

    for sensedState, trueState in zip(sensed_history, truth_history):
        if trueState == 1:  # true alarm
            if sensedState == 0:  # sensed fail
                true_alarm_sensed_fail += 1
            elif sensedState == 2:  # sensed working
                true_alarm_sensed_working += 1

    return true_alarm_sensed_fail, true_alarm_sensed_working

def countMissedWorkings(truth_history, sensed_history):
    """
    Determine all missed workings
    """
    true_working_sensed_fail = 0
    true_working_sensed_alarm = 0

    for sensedState, trueState in zip(sensed_history, truth_history):
        if trueState == 2:  # true working
            if sensedState == 0:  # sensed fail
                true_working_sensed_fail += 1
            elif sensedState == 1:  # sensed alarm
                true_working_sensed_alarm += 1

    return true_working_sensed_fail, true_working_sensed_alarm

# --- Function to create a multi-simulation results table ---



# --- Plotting function for confusion matrix ---
def plot_confusion_matrix(cm_mean, param, num_simulations, simulation_hours):
    """
    Plot the averaged confusion matrix for a given parameter set.
    """
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm_mean, annot=True, fmt=".2f", cmap="BuPu",
                xticklabels=["Fail", "Alarm", "Working"],
                yticklabels=["Fail", "Alarm", "Working"], cbar=False)
    plt.title(f"Average Confusion Matrix \nNum Simulations: {num_simulations}, Hours: {simulation_hours},\nSensors: {param[0]}, Quality: {param[1]}")
    plt.xlabel("Sensed")
    plt.ylabel("Truth")
    plt.tight_layout()
    plt.savefig(f"confusionMatrices/{num_simulations}Ships/confusion_matrix_({param[0]}_'{param[1]}')_{num_simulations}ships_{simulation_hours}Hrs.png", dpi=300)
    plt.close()