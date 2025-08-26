from shipClass.Component import Component
from shipClass.Sensor2 import Sensor
from utils.helperFunctions import find_mode

from tabulate import tabulate

import matplotlib.pyplot as plt

class SensedComp():

    """ A collection of functions for a component with attached sensors"""

    def __init__(self, component: Component, sensors: list[Sensor]):
        self.component = component
        self.sensors = sensors
        self.sensedState = self.senseState()
        self.history =[self.sensedState]  # history of the sensed states

# -------------------- Simulation Functions -----------------------------
    def senseState (self): 
        sensor_readings = [None for _ in self.sensors]  # store the sensor readings
        for j, sensor in enumerate(self.sensors):
            sensor.read(self.component.state, len(self.component.history)) # allow the sensor to read the component state
            sensor_readings[j] = sensor.history[-1]  # append the latest sensor reading to the list

        aggregated_reading = find_mode(sensor_readings) # aggregate the sensor readings
        sensedState = aggregated_reading
        return sensedState


    def simulate(self, number_of_steps = 1):
        for i in range(number_of_steps):
            self.component.simulate(1)
            self.history.append(self.senseState())


# ---------------------- Plotting Functions -----------------------------
    def plotHistory(self):
        ax= self.component.plotHistory()

        for sensor in self.sensors:
           sensor.plotReadings(ax)  
        
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5)) # Place legend to the right, centered vertically
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

        SM_aggregate = 0
        FN_aggregate = 0
        FP_aggregate = 0
        FA_aggregate = 0
        MA_aggregate = 0

        for i in range(len(self.component.history)-1):
            # Overall Sensor Malfunction
            if self.history[i] != self.component.history[i]:
                SM_aggregate += 1

            # Overall False Negatives
            if self.history[i] == 0 and self.component.history[i] == 2:
                FN_aggregate += 1

            # Overall False Positives
            if self.history[i] == 2 and self.component.history[i] == 0:
                FP_aggregate += 1

            # Overall False Alarms
            if self.history[i] == 1 and self.component.history[i] == 2:
                FA_aggregate += 1

            # Overall Missed Alarms
            if self.history[i] == 2 and self.component.history[i] == 1:
                MA_aggregate += 1


        headers = ["Sensor", "SM", "FN", "FP", "FA", "MA"]
        rows = zip(sensor_num, SM_counts, FN_counts, FP_counts, FA_counts, MA_counts)
        aggregate_row = ["Aggregate", SM_aggregate, FN_aggregate, FP_aggregate, FA_aggregate, MA_aggregate]
        print(tabulate([headers] + list(rows) + [aggregate_row], headers="firstrow"))