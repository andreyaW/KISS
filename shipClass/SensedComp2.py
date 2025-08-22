from shipClass.Component import Component
from shipClass.Sensor2 import Sensor

from tabulate import tabulate


import matplotlib.pyplot as plt

class SensedComp():

    """ A collection of functions for a component with attached sensors"""

    def __init__(self, component: Component, sensors: list[Sensor]):
        self.component = component
        self.sensors = sensors

# -------------------- Simulation Functions -----------------------------
    def simulate(self, number_of_steps = 1):
        for i in range(number_of_steps):
            for sensor in self.sensors:
                sensor.read(self.component.state, len(self.component.history)) # allow the sensor to read the component state
            self.component.simulate(1)

# ---------------------- Plotting Functions -----------------------------
    def plotHistory(self):
        ax= self.component.plotHistory()

        for sensor in self.sensors:
           sensor.plotReadings(ax)  
        
        plt.legend()
        plt.show()
        

    def summaryOfReadings(self):
        """
        Check for any incorrect sensor readings compared to the true health state of the component.
        Types of wrong readings: 
            1. Sensor Malfunction (SM): Sensor reading is incorrect 
            2. False Negatives (FN): Sensor indicates "Major Fail" but true state is "Working"
            3. False Positives (FP): Sensor indicates "Working" but true state is "Major Fail"
            4. False Alarms (FA): Sensor indicates "Minor Fail" but true state is "Working"
            5. Missed Alarms (MA): Sensor indicates "Working" but true state is "Minor Fail"
        """
        sensor_num = [i+1 for i in range(len(self.sensors))]
        SM_counts = [0 for _ in self.sensors]
        FN_counts = [0 for _ in self.sensors]
        FP_counts = [0 for _ in self.sensors]
        FA_counts = [0 for _ in self.sensors]
        MA_counts = [0 for _ in self.sensors]
        for i, sensor in enumerate(self.sensors):
            SM_count, FN_count, FP_count, FA_count, MA_count = sensor.checkReadings(self.component)
            SM_counts[i] = SM_count
            FN_counts[i] = FN_count
            FP_counts[i] = FP_count
            FA_counts[i] = FA_count
            MA_counts[i] = MA_count

        headers = ["Sensor", "SM", "FN", "FP", "FA", "MA"]
        rows = zip(sensor_num, SM_counts, FN_counts, FP_counts, FA_counts, MA_counts)
        print(tabulate([headers] + list(rows), headers="firstrow"))