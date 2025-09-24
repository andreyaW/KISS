# my sensor class (less efficient)
import numpy as np
import matplotlib.pyplot as plt
import random

class Sensor:
    def __init__(self, quality='Good'):
        """
        Parameters: 
        ---------------------
        quality: str
            The quality of the sensor (e.g., 'good', 'moderate', or 'bad').
        """
        self.quality = quality
        self.state = 1  # 1 = working, 0 = faulty
        self.history = []  # history of the current state of the sensor
        self.sensedHistory = []  # history of the sensor readings
        self.observation_probs = self.setObservationProbs()
        # self.sensing_interval = 30  # seconds

    def setObservationProbs(self):
        """ set the observation probabilities based on sensor quality """
        if self.quality == 'good':
            percent_accurate= 98
            remaining = 100 - percent_accurate
            per_wrong = remaining / 2
            observation_probs = np.array([[0.98, 0.01, 0.01],
                                          [0.01, 0.98, 0.01],
                                          [0.01, 0.01, 0.98]])
        elif self.quality == 'moderate':
            observation_probs = np.array([[0.75, 0.125, 0.125],
                                          [0.125, 0.75, 0.125],
                                          [0.125, 0.125, 0.75]])
        elif self.quality == 'bad':
            observation_probs = np.array([[0.5, 0.25, 0.25],
                                          [0.25, 0.5, 0.25],
                                          [0.25, 0.25, 0.5]])
        else: 
            raise ValueError("Invalid sensor quality. Choose from 'good', 'moderate', or 'bad'.")
        return observation_probs

    # # OLD READ FUNCTION
    # def read(self, true_health_reading):
    #     """
    #     Simulates a sensor reading.
    #     Returns either the correct health reading or an incorrect one based on the observation probabilities
    #     """
    #     # if (step_num-1) % self.sensing_interval != 0:
    #     #     self.sensed_history.append(self.sensed_history[-1])  # Maintain last reading if not sensing
    #     # else:
        
    #     # Get the observation probabilities for the true health reading
    #     probs = self.observation_probs[true_health_reading]

    #     # Simulate the sensor reading based on the probabilities
    #     reading = np.random.choice([0, 1, 2], p=probs)
    #     self.sensedHistory.append(reading)

    #     if self.sensedHistory[-1] != true_health_reading:
    #         self.state = 0 # sensor is faulty
    #     else:
    #         self.state = 1 # sensor is working
    #     self.history.append(self.state)

    # NEW READ FUNCTION
    def read(self, true_health_reading):
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
        r = np.random.rand()
        reading = np.searchsorted(np.cumsum(probs), r)
        self.sensedHistory.append(reading)

        if self.sensedHistory[-1] != true_health_reading:
            self.state = 0 # sensor is faulty
        else:
            self.state = 1 # sensor is working
        self.history.append(self.state)

    def simulate(self, true_health_readings):
        n_steps = len(true_health_readings)

        # Preallocate once if not done yet
        if not hasattr(self, 'history') or len(self.history) < self.step_counter + n_steps:
            new_size = self.step_counter + n_steps
            hist = np.empty(new_size, dtype=int)
            sensed = np.empty(new_size, dtype=int)

            if hasattr(self, 'history'):
                hist[:self.step_counter] = self.history[:self.step_counter]
                sensed[:self.step_counter] = self.sensedHistory[:self.step_counter]

            self.history = hist
            self.sensedHistory = sensed

        # Fill in the new segment
        for i, state in enumerate(true_health_readings):
            r = np.random.rand()
            probs = self.observation_probs[state]
            reading = np.searchsorted(np.cumsum(probs), r)
            self.sensedHistory[self.step_counter] = reading
            self.history[self.step_counter] = 1 if reading == state else 0
            self.step_counter += 1

    def reset(self):
        """Resets the sensor to its initial state."""
        self.history = []
        self.sensedHistory = []


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
        readings = np.array(self.sensedHistory)
        true = np.array(component.history)

        SM = np.sum(readings != true)
        FN = np.sum((readings == 0) & (true == 2))
        FP = np.sum((readings == 2) & (true == 0))
        FA = np.sum((readings == 1) & (true == 2))
        MA = np.sum((readings == 2) & (true == 1))

        return SM, FN, FP, FA, MA
    
