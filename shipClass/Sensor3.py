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
        self.history = []
        self.setObservationProbs()
        self.sensing_interval = 5  # seconds

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
        if (step_num-1) % self.sensing_interval != 0:
            self.history.append(self.history[-1])  # Maintain last reading if not sensing
        else:
            # Get the observation probabilities for the true health reading
            probs = self.observation_probs[true_health_reading]

            # Simulate the sensor reading based on the probabilities
            reading = np.random.choice([0, 1, 2], p=probs)
            self.history.append(reading)

# ---------------------- Plotting Functions -----------------------------
    def plotReadings(self, ax):
        # Plot the sensor readings over time on a given axis
        ax.plot(self.history, label=f"Sensor (Quality: {self.quality})")



# ------------------ Simulation Functions -----------------------------
def checkReadings(self, component):
        SM_count = 0
        FN_count = 0
        FP_count = 0
        FA_count = 0
        MA_count = 0
        
        return SM_count, FN_count, FP_count, FA_count, MA_count