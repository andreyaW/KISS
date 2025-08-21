import random
import matplotlib.pyplot as plt

class Sensor:
    def __init__(self, degradation_level=0.0):
        """
        degradation_level: float between 0 (new) and 1 (fully degraded)
        """
        self.degradation_level = degradation_level
        self.history = []
        
    def read(self, true_health_reading):
        """
        Simulates a sensor reading.
        Returns either the correct health reading or an incorrect one based on degradation.
        """
        # Probability of correct reading decreases as degradation increases
        prob_correct = 1.0 - self.degradation_level
        if random.random() < prob_correct:
            return true_health_reading  # Correct reading
        else:
            # Simulate incorrect reading (e.g., random noise or offset)
            noise = random.uniform(-1, 1) * self.degradation_level
            reading = round(true_health_reading + noise)
        self.history.append(reading)
        return reading

# ---------------------- Plotting Functions -----------------------------
    def plotReadings(self, ax):
        # Plot the sensor readings over time on a given axis
        ax.plot(self.history, label=f"Sensor (Degradation Level: {self.degradation_level})")
        return ax