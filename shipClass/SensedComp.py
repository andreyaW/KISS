from shipClass.Component import Component
from shipClass.Sensor_basic import Sensor
from utils.helperFunctions import find_mode
from tabulate import tabulate
from utils.excelFunctions import addUnsensedFailureFormula, addSensorFailureFormula, finalFormatting

import xlsxwriter
import matplotlib.pyplot as plt
import numpy as np

class SensedComp:

    """A component with attached sensors."""

    def __init__(self, component: Component, sensors: list[Sensor]):
        self.comp = component
        self.sensors = sensors
        self.sensedHistory = np.array([], dtype=int)

        # Initialize sensors with component's current state
        for sensor in self.sensors:
            sensor.sensedHistory = np.array([self.comp.state], dtype=int)
            sensor.history = np.array([1], dtype=int) # assumes sensors are working at start
        self.sensedState = self.comp.state
        self.sensedHistory = np.array([self.sensedState], dtype=int)
        
    # -------------------- Simulation Functions -----------------------------
    def simulate(self, num_steps=1):
        """Simulate the sensed component and its sensors over multiple steps."""
        # Simulate component once
        self.comp.simulate(num_steps)
        true_health_readings = self.comp.history[-num_steps:]

        # Simulate all sensor readings for the new steps
        for sensor in self.sensors:
            sensor.read(true_health_readings)

        # Aggregate sensor readings
        sensor_matrix = np.array([sensor.sensedHistory[-num_steps:] for sensor in self.sensors])
        sensor_readings = np.empty(num_steps, dtype=int)
        for t in range(num_steps):
            sensor_readings[t] = find_mode(sensor_matrix[:, t])
        self.sensedHistory = np.concatenate([self.sensedHistory, sensor_readings])

    def reset(self):
        """Reset component and sensors."""
        self.comp.reset()
        for sensor in self.sensors:
            sensor.reset()
        # assume sensors read the initial state correctly
        self.sensedState = self.comp.state
        self.sensedHistory = np.array([self.sensedState], dtype=int)

    # ---------------------- Plotting Functions -----------------------------
    def plotHistory(self):
        ax = self.comp.plotHistory()
        for sensor in self.sensors:
            sensor.plotReadings(ax)
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.show()

    # ---------------------- Excel Export Functions -------------------------
    def printHistory2Excel(self, filename: str, worksheet=None):
        """Print the history of the sensed component and its sensors to Excel."""
        num_steps = len(self.sensedHistory)

        with xlsxwriter.Workbook(filename) as workbook:
            if worksheet is None:
                sheet_name = self.comp.name[:31]
                worksheet = workbook.add_worksheet(sheet_name)

            # Time steps
            worksheet.write(0, 0, "Time Step")
            worksheet.write_column(1, 0, np.arange(num_steps))

            # True states
            worksheet.write(0, 1, "Comp Truth State")
            worksheet.write_column(1, 1, self.comp.history)

            # Sensor states
            for j, sensor in enumerate(self.sensors):
                worksheet.write(0, j+2, f"Sensor {j+1} State")
                worksheet.write_column(1, j+2, sensor.history)

            # Sensed aggregated states
            col_offset = len(self.sensors) + 2
            worksheet.write(0, col_offset, "Comp Sensed State")
            worksheet.write_column(1, col_offset, self.sensedHistory)
            for j, sensor in enumerate(self.sensors):
                worksheet.write(0, col_offset + j + 1, f"Sensor {j+1} Reading")
                worksheet.write_column(1, col_offset + j + 1, sensor.sensedHistory)

            # Add formulas for performance
            truth_col = 1
            sensed_col = col_offset
            f1_col = sensed_col + len(self.sensors) + 1
            f2_col = f1_col + 1
            for i in range(num_steps):
                addUnsensedFailureFormula(workbook, worksheet, i, truth_col, sensed_col, f1_col, num_steps)
                addSensorFailureFormula(workbook, worksheet, i, truth_col, f2_col, num_steps, len(self.sensors))

            finalFormatting(worksheet, 1)

    # ---------------------- Summary of Readings ---------------------------
    def summaryOfReadings(self):
        """Vectorized computation of sensor reading errors compared to true component state."""
        comp_history = np.array(self.comp.history)
        sensed_history = np.array(self.sensedHistory)
        n_sensors = len(self.sensors)

        SM_counts = np.array([np.sum(np.array(sensor.sensedHistory) != comp_history) for sensor in self.sensors])
        FN_counts = np.array([np.sum((np.array(sensor.sensedHistory) == 0) & (comp_history == 2)) for sensor in self.sensors])
        FP_counts = np.array([np.sum((np.array(sensor.sensedHistory) == 2) & (comp_history == 0)) for sensor in self.sensors])
        FA_counts = np.array([np.sum((np.array(sensor.sensedHistory) == 1) & (comp_history == 2)) for sensor in self.sensors])
        MA_counts = np.array([np.sum((np.array(sensor.sensedHistory) == 2) & (comp_history == 1)) for sensor in self.sensors])

        SM_aggregate = np.sum(sensed_history != comp_history)
        FN_aggregate = np.sum((sensed_history == 0) & (comp_history == 2))
        FP_aggregate = np.sum((sensed_history == 2) & (comp_history == 0))
        FA_aggregate = np.sum((sensed_history == 1) & (comp_history == 2))
        MA_aggregate = np.sum((sensed_history == 2) & (comp_history == 1))

        headers = ["Sensor", "SM", "FN", "FP", "FA", "MA"]
        rows = zip(range(1, n_sensors + 1), SM_counts, FN_counts, FP_counts, FA_counts, MA_counts)
        aggregate_row = ["Aggregate", SM_aggregate, FN_aggregate, FP_aggregate, FA_aggregate, MA_aggregate]

        print(tabulate([headers] + list(rows) + [aggregate_row], headers="firstrow"))
