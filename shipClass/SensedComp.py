from shipClass.Component import Component
from shipClass.old_Model.Sensor2 import Sensor
from utils.helperFunctions import find_mode
from tabulate import tabulate
from utils.excelFunctions import addTimeSteps, addTruth, addSensed, addUnsensedFailureFormula, addSensorFailureFormula, finalFormatting

import xlsxwriter
import matplotlib.pyplot as plt
import numpy as np


# MY SENSED COMPONENT:
class SensedComp():

    """ A collection of functions for a component with attached sensors"""

    def __init__(self, component: Component, sensors: list[Sensor]):
        self.comp = component
        self.sensors = sensors
        self.sensedHistory = []
        self.senseState()

# -------------------- Simulation Functions -----------------------------
    def senseState (self): 
        sensor_readings = [None for _ in self.sensors]  # store the sensor readings
        for j, sensor in enumerate(self.sensors):
            sensor.read(self.comp.state) # allow the sensor to read the component state
            sensor_readings[j] = sensor.sensedHistory[-1]  # append the latest sensor reading to the list

        aggregated_reading = find_mode(sensor_readings) # aggregate the sensor readings
        sensedState = aggregated_reading
        
        # update the sensed state and its history
        self.sensedState =  sensedState
        self.sensedHistory.append(sensedState)

    def simulate(self, number_of_steps = 1):

        """ Simulate the sensed component and its sensors over n steps """

        for i in range(number_of_steps):
            self.comp.simulate(1)
            self.senseState()

    def reset(self):
        """Resets the sensed component to its initial state."""
        self.comp.reset()
        for sensor in self.sensors:
            sensor.reset()
        self.sensedHistory = []
        self.senseState()

# ---------------------- Plotting Functions -----------------------------
    def plotHistory(self):
        ax= self.comp.plotHistory()

        for sensor in self.sensors:
           sensor.plotReadings(ax)  
        
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5)) # Place legend to the right, centered vertically
        plt.show()
        

    def printHistory2Excel(self, filename: str, worksheet: str = None):
        """ print the history of the sensed component and its sensors to an excel sheet """
       
        with xlsxwriter.Workbook(filename) as workbook:
            if worksheet is None:
                if len(self.comp.name) > 31:
                    sheet_name = self.comp.name[:31]
                else: 
                    sheet_name = self.comp.name
                worksheet = workbook.add_worksheet(sheet_name)

            num_data = len(self.sensedHistory)
            for i in range(num_data):
                # add the time steps to the first column
                addTimeSteps(workbook, worksheet, i)

                # add true states of the component and each sensor to the row
                truth_data = [self.comp.history[i]] + [sensor.history[i] for sensor in self.sensors]

                if i == 0:
                    comp_truth_headers = ['Comp Truth State'] + [f'Sensor {j+1} State' for j in range(len(self.sensors))]
                    addTruth(workbook, worksheet, i, truth_data, comp_truth_headers)
                else:
                    addTruth(workbook, worksheet, i, truth_data)

                # add sensed states of the component and each sensor to the row
                comp_sensed_state = self.sensedHistory[i]
                sensor_readings = [sensor.sensedHistory[i] for sensor in self.sensors]
                sensed_states = [comp_sensed_state] + sensor_readings
                if i == 0:
                    sensed_headers = ['Comp Sensed State'] + [f'Sensor {j+1} Reading' for j in range(len(self.sensors))]
                    addSensed(workbook, worksheet, i, sensed_states, sensed_headers)
                else:
                    addSensed(workbook, worksheet, i, sensed_states)

            # add formulas for checking sensor performance to end of each row
                truth_col = 2  # column index for component truth state
                sensed_col = truth_col + len(self.sensors) + 1  # column index for component sensed state
                f1_col = sensed_col + len(self.sensors) + 1  # column index for first formula
                f2_col = f1_col + 1  # column index for second formula
                
                # add formula to check if sensed state matches truth state
                addUnsensedFailureFormula(workbook, worksheet, i, truth_col, sensed_col, f1_col, num_data)

                # add formula to check if sensors are in a faulty state
                addSensorFailureFormula(workbook, worksheet, i, truth_col, f2_col, num_data, len(self.sensors))
            
            # format the worksheet for easy viewing
            finalFormatting(worksheet, 1)



    def summaryOfReadings(self):
        """
        Efficiently compute sensor reading statistics compared to the true component state.
        """

        # Convert histories to NumPy arrays for fast vectorized operations
        comp_history = np.array(self.comp.history)
        sensed_history = np.array(self.sensedHistory)

        n_sensors = len(self.sensors)
        sensor_num = np.arange(1, n_sensors + 1)

        # Preallocate arrays for individual sensor counts
        SM_counts = np.zeros(n_sensors, dtype=int)
        FN_counts = np.zeros(n_sensors, dtype=int)
        FP_counts = np.zeros(n_sensors, dtype=int)
        FA_counts = np.zeros(n_sensors, dtype=int)
        MA_counts = np.zeros(n_sensors, dtype=int)

        # Compute per-sensor statistics using vectorized operations
        for i, sensor in enumerate(self.sensors):
            sensor_readings = np.array(sensor.sensedHistory)
            SM_counts[i] = np.sum(sensor_readings != comp_history)
            FN_counts[i] = np.sum((sensor_readings == 0) & (comp_history == 2))
            FP_counts[i] = np.sum((sensor_readings == 2) & (comp_history == 0))
            FA_counts[i] = np.sum((sensor_readings == 1) & (comp_history == 2))
            MA_counts[i] = np.sum((sensor_readings == 2) & (comp_history == 1))

        # Compute aggregate counts across all sensor readings
        SM_aggregate = np.sum(sensed_history != comp_history)
        FN_aggregate = np.sum((sensed_history == 0) & (comp_history == 2))
        FP_aggregate = np.sum((sensed_history == 2) & (comp_history == 0))
        FA_aggregate = np.sum((sensed_history == 1) & (comp_history == 2))
        MA_aggregate = np.sum((sensed_history == 2) & (comp_history == 1))

        # Display results
        headers = ["Sensor", "SM", "FN", "FP", "FA", "MA"]
        rows = zip(sensor_num, SM_counts, FN_counts, FP_counts, FA_counts, MA_counts)
        aggregate_row = ["Aggregate", SM_aggregate, FN_aggregate, FP_aggregate, FA_aggregate, MA_aggregate]

        print(tabulate([headers] + list(rows) + [aggregate_row], headers="firstrow"))

