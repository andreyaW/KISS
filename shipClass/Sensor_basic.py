import numpy as np
import matplotlib.pyplot as plt
import random

class Sensor:
    def __init__(self, quality='Good'):
        """
        Parameters: 
        ---------------------
        quality: str
            The quality of the sensor (e.g., 'Good', 'Moderate', or 'Bad').
        """
        self.quality = quality
        self.state = 1  # 1 = working, 0 = faulty
        self.history = []  # history of the current state of the sensor
        self.sensedHistory = []  # history of the sensor readings
        self.setObservationProbs()
        self.sensing_interval = 30  # seconds

    def setObservationProbs(self):
        """ set the observation probabilities based on sensor quality """
        if self.quality == 'Good':
            observation_probs = np.array([[0.98, 0.01, 0.01],
                                          [0.01, 0.98, 0.01],
                                          [0.01, 0.01, 0.98]])
        elif self.quality == 'Moderate':
            observation_probs = np.array([[0.75, 0.125, 0.125],
                                          [0.125, 0.75, 0.125],
                                          [0.125, 0.125, 0.75]])
        elif self.quality == 'Bad':
            observation_probs = np.array([[0.5, 0.25, 0.25],
                                          [0.25, 0.5, 0.25],
                                          [0.25, 0.25, 0.5]])
        self.observation_probs = observation_probs


    def read(self, true_health_reading, step_num):
        """
        Simulates a sensor reading.
        Returns either the correct health reading or an incorrect one based on the observation probabilities
        """
        # if (step_num-1) % self.sensing_interval != 0:
        #     self.sensed_history.append(self.sensed_history[-1])  # Maintain last reading if not sensing
        # else:
        
        # Get the observation probabilities for the true health reading
        probs = self.observation_probs[true_health_reading]

        # Simulate the sensor reading based on the probabilities
        reading = np.random.choice([0, 1, 2], p=probs)
        self.sensedHistory.append(reading)

        if self.sensedHistory[-1] != true_health_reading:
            self.state = 0 # sensor is faulty
        else:
            self.state = 1 # sensor is working
        self.history.append(self.state)


    def reset(self):
        """Resets the sensor to its initial state."""
        self.history = []
        self.sensedHistory = []
        # self.history = [self.history[0]]
        # self.sensedHistory = [self.sensedHistory[0]]


# ---------------------- Plotting Functions -----------------------------
    def plotReadings(self, ax):
        # Plot the sensor readings over time on a given axis
        ax.plot(self.sensedHistory, marker= '*',linestyle='', label=f"Sensor (Quality: {self.quality})")

# ------------------ Simulation Functions -----------------------------
    def checkReadings(self, component):
        """
        Check for any incorrect sensor readings compared to the true health state of the component.
        Types of wrong readings: 
            1. Sensor Malfunction (SM): Sensor reading is incorrect 
            2. False Negatives (FN): Sensor indicates "Major Fail" but true state is "Working"
            3. False Positives (FP): Sensor indicates "Working" but true state is "Major Fail"
            4. False Alarms (FA): Sensor indicates "Minor Fail" but true state is "Working"
            5. Missed Alarms (MA): Sensor indicates "Working" but true state is "Minor Fail"
        """
        SM_count = 0
        FN_count = 0
        FP_count = 0
        FA_count = 0
        MA_count = 0

        for i, reading in enumerate(self.sensedHistory):
            # Sensor Malfunction
            if reading != component.history[i]:
                SM_count += 1
            # False Negatives
            if reading == 0 and component.history[i] == 2:
                FN_count += 1
            # False Positives
            if reading == 2 and component.history[i] == 0:
                FP_count += 1
            # False Alarms
            if reading == 1 and component.history[i] == 2:
                FA_count += 1
            # Missed Alarms
            if reading == 2 and component.history[i] == 1:
                MA_count += 1

        return SM_count, FN_count, FP_count, FA_count, MA_count