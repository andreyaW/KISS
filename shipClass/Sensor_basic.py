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
        self.history = np.array([], dtype=int)          # state history: 1 for working, 0 for failed
        self.sensedHistory = np.array([], dtype=int)    # sensor readings
        self.observation_probs = self.setObservationProbs()
        # self.sensing_interval = 30  # seconds

    def setObservationProbs(self):
        """ set the observation probabilities based on sensor quality """
        quality = self.quality.lower()

        if quality == 'good':
            observation_probs = np.array([[0.98, 0.01, 0.01],
                                          [0.01, 0.98, 0.01],
                                          [0.01, 0.01, 0.98]])
        elif quality == 'moderate':
            observation_probs = np.array([[0.75, 0.125, 0.125],
                                          [0.125, 0.75, 0.125],
                                          [0.125, 0.125, 0.75]])
        elif quality == 'bad':
            observation_probs = np.array([[0.5, 0.25, 0.25],
                                          [0.25, 0.5, 0.25],
                                          [0.25, 0.25, 0.5]])
        return observation_probs

    def read(self, true_history):
        """
        Vectorized simulation of multiple sensor readings at once using np.random.choice.
        """
        n = len(true_history)
        sensed = np.empty(n, dtype=int)

        # For each possible true state, sample all readings at once
        for state in range(self.observation_probs.shape[0]):
            mask = true_history == state
            if np.any(mask):
                sensed[mask] = np.random.choice(
                    [0, 1, 2],
                    size=mask.sum(),
                    p=self.observation_probs[state]
                )

        # Sensor working history: 1 if match, 0 if not
        working = (sensed == true_history).astype(int)

        # Update histories
        self.sensedHistory = np.concatenate([self.sensedHistory, sensed])
        self.history = np.concatenate([self.history, working])


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
        Vectorized check for incorrect sensor readings compared to the true health state.
        """
        readings = np.asarray(self.history)
        true_states = np.asarray(component.history)

        # Masks
        SM = readings != true_states
        FN = (readings == 0) & (true_states == 2)
        FP = (readings == 2) & (true_states == 0)
        FA = (readings == 1) & (true_states == 2)
        MA = (readings == 2) & (true_states == 1)

        return SM.sum(), FN.sum(), FP.sum(), FA.sum(), MA.sum()
