
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

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
def plot_confusion_matrix(save_path, 
                          c00, c01, c02,
                          c10, c11, c12,
                          c20, c21, c22,
                          labels=None,
                          cmap="RdBu"):
    """
    Plot a 3x3 confusion matrix with provided cell values.

    Parameters
    ----------
    c00 ... c22 : int
        Values for the 9 cells (row-major order).
    labels : list of str, optional
        Class labels for axes.
    cmap : str
        Colormap for heatmap.
    """
    # Build matrix
    cm = np.array([
        [c00, c01, c02],
        [c10, c11, c12],
        [c20, c21, c22]
    ])

    # Default labels if none provided
    if labels is None:
        labels = [f"Class {i}" for i in range(3)]

    # Plot heatmap
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt=".2f", cmap=cmap, 
                xticklabels=labels, yticklabels=labels, cbar=False)

    plt.title("Confusion Matrix")
    plt.xlabel("Sensed")
    plt.ylabel("Truth")
    plt.tight_layout()

    # # Ensure directory exists
    # os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Save and close
    plt.savefig(save_path, dpi=300)
    plt.close()