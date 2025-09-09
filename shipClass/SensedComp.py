from shipClass.Component import Component
from shipClass.old_Model.Sensor2 import Sensor
from utils.helperFunctions import find_mode
from tabulate import tabulate
from utils.excelFunctions import addTimeSteps, addTruth, addSensed, addUnsensedFailureFormula, addSensorFailureFormula, finalFormatting

import xlsxwriter
import matplotlib.pyplot as plt

class SensedComp():

    """ A collection of functions for a component with attached sensors"""

    def __init__(self, component: Component, sensors: list[Sensor]):
        self.component = component
        self.sensors = sensors
        self.sensedState = self.senseState()
        self.sensedHistory = [self.sensedState]  # history of the sensed states

# -------------------- Simulation Functions -----------------------------
    def senseState (self): 
        sensor_readings = [None for _ in self.sensors]  # store the sensor readings
        for j, sensor in enumerate(self.sensors):
            sensor.read(self.component.state, len(self.component.history)) # allow the sensor to read the component state
            sensor_readings[j] = sensor.sensedHistory[-1]  # append the latest sensor reading to the list

        aggregated_reading = find_mode(sensor_readings) # aggregate the sensor readings
        sensedState = aggregated_reading
        return sensedState


    def simulate(self, number_of_steps = 1):
        for i in range(number_of_steps):
            self.component.simulate(1)
            self.sensedState = self.senseState()
            self.sensedHistory.append(self.sensedState)

    def reset(self):
        """Resets the sensed component to its initial state."""
        self.component.reset()
        for sensor in self.sensors:
            sensor.reset()
        self.sensedState = self.senseState()
        self.sensedHistory = [self.sensedState]

# ---------------------- Plotting Functions -----------------------------
    def plotHistory(self):
        ax= self.component.plotHistory()

        for sensor in self.sensors:
           sensor.plotReadings(ax)  
        
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5)) # Place legend to the right, centered vertically
        plt.show()
        

    def printHistory2Excel(self, filename: str, worksheet: str = None):
        """ print the history of the sensed component and its sensors to an excel sheet """
       
        with xlsxwriter.Workbook(filename) as workbook:
            if worksheet is None:
                if len(self.component.name) > 31:
                    sheet_name = self.component.name[:31]
                else: 
                    sheet_name = self.component.name
                worksheet = workbook.add_worksheet(sheet_name)

            num_data = len(self.sensedHistory)
            for i in range(num_data):
                # add the time steps to the first column
                addTimeSteps(workbook, worksheet, i)

                # add true states of the component and each sensor to the row
                truth_data = [self.component.history[i]] + [sensor.history[i] for sensor in self.sensors]

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
        Check for any incorrect sensor readings compared to the true health state of the component.
        Types of wrong readings: 
            1. Sensor Malfunction (SM): Sensor reading is incorrect 
            2. False Negatives (FN): Sensor indicates "Major Fail" but true state is "Working"
            3. False Positives (FP): Sensor indicates "Working" but true state is "Major Fail"
            4. False Alarms (FA): Sensor indicates "Minor Fail" but true state is "Working"
            5. Missed Alarms (MA): Sensor indicates "Working" but true state is "Minor Fail"
        """
        # get the counts for each individual sensor
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

        # get the counts for the aggregate of all sensor readings
        SM_aggregate = 0
        FN_aggregate = 0
        FP_aggregate = 0
        FA_aggregate = 0
        MA_aggregate = 0
        for i in range(len(self.component.history)-1):
            # Overall Sensor Malfunction
            if self.sensedHistory[i] != self.component.history[i]:
                SM_aggregate += 1

            # Overall False Negatives
            if self.sensedHistory[i] == 0 and self.component.history[i] == 2:
                FN_aggregate += 1

            # Overall False Positives
            if self.sensedHistory[i] == 2 and self.component.history[i] == 0:
                FP_aggregate += 1

            # Overall False Alarms
            if self.sensedHistory[i] == 1 and self.component.history[i] == 2:
                FA_aggregate += 1

            # Overall Missed Alarms
            if self.sensedHistory[i] == 2 and self.component.history[i] == 1:
                MA_aggregate += 1

        headers = ["Sensor", "SM", "FN", "FP", "FA", "MA"]
        rows = zip(sensor_num, SM_counts, FN_counts, FP_counts, FA_counts, MA_counts)
        aggregate_row = ["Aggregate", SM_aggregate, FN_aggregate, FP_aggregate, FA_aggregate, MA_aggregate]
        print(tabulate([headers] + list(rows) + [aggregate_row], headers="firstrow"))