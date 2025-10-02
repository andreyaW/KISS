
def countRightAndWrongReadings(truth_history, sensed_history):
    """
    Determine all correct and incorrect sensor readings
    """

    # correct vs incorrect readings
    correct_readings = 0
    incorrect_readings = 0

    for sensedState, trueState in zip(sensed_history, truth_history):
        if sensedState == trueState:
            correct_readings += 1
        else:
            incorrect_readings += 1

    return correct_readings, incorrect_readings

def countFalseNegatives(truth_history, sensed_history):
    """
    Determine all false negatives (missed failures and false alarms)
    A false negative is when the true state is a failure (0) but the sensed state is not a failure (not 0).
    """
    false_fails = 0         # truth != 0 ; sensed = 0
    false_alarms = 0        # truth != 1 ; sensed = 1

    for sensedState, trueState in zip(sensed_history, truth_history):
        if trueState != 0 and sensedState == 0:
            false_fails += 1
        if trueState != 1 and sensedState == 1:
            false_alarms += 1

    return false_fails, false_alarms