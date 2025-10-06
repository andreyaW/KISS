from shipClass.Component import Component
from shipClass.Sensor_basic import Sensor
from utils.helperFunctions import find_mode
from tabulate import tabulate
from utils.excelFunctions import addUnsensedFailureFormula, addSensorFailureFormula, finalFormatting

import xlsxwriter
import matplotlib.pyplot as plt
import numpy as np

# class SensedComp:

#     """A component with attached sensors."""

#     def __init__(self, component: Component, sensors: list[Sensor]):
#         self.comp = component
#         self.sensors = sensors
#         self.sensedHistory = np.array([], dtype=int)

#         # Initialize sensors with component's current state
#         for sensor in self.sensors:
#             sensor.sensedHistory = np.array([self.comp.state], dtype=int)
#             sensor.history = np.array([1], dtype=int) # assumes sensors are working at start
#         self.sensedState = self.comp.state
#         self.sensedHistory = np.array([self.sensedState], dtype=int)
        
#     # -------------------- Simulation Functions -----------------------------
#     def simulate(self, num_steps=1):
#         """Simulate the sensed component and its sensors over multiple steps (fully vectorized)."""
#         # Simulate the component itself
#         self.comp.simulate(num_steps)
#         true_health_readings = self.comp.history[-num_steps:]

#         # Simulate all sensor readings
#         for sensor in self.sensors:
#             sensor.read(true_health_readings)

#         # Stack sensor readings: shape (n_sensors, num_steps)
#         sensor_matrix = np.vstack([sensor.sensedHistory[-num_steps:] for sensor in self.sensors])

#         # One-hot encode sensor readings for all states: shape (n_sensors, num_steps, n_states)
#         n_states = 3
#         one_hot = np.eye(n_states)[sensor_matrix]  # shape -> (n_sensors, num_steps, 3)

#         # Sum across sensors to get counts per state per timestep: shape -> (num_steps, n_states)
#         counts = one_hot.sum(axis=0)

#         # Majority vote across sensors
#         sensor_readings = counts.argmax(axis=1)  # shape -> (num_steps,)

#         # Append to history
#         self.sensedHistory = np.concatenate([self.sensedHistory, sensor_readings])
        

#     def reset(self):
#         """Reset component and sensors."""
#         self.comp.reset()
#         for sensor in self.sensors:
#             sensor.reset()
#         # assume sensors read the initial state correctly
#         self.sensedState = self.comp.state
#         self.sensedHistory = np.array([self.sensedState], dtype=int)

#     # ---------------------- Plotting Functions -----------------------------
#     def plotHistory(self):
#         ax = self.comp.plotHistory()
#         for sensor in self.sensors:
#             sensor.plotReadings(ax)
#         ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#         plt.show()

#     # ---------------------- Excel Export Functions -------------------------
#     def printHistory2Excel(self, filename: str, worksheet=None):
#         """Print the history of the sensed component and its sensors to Excel."""
#         num_steps = len(self.sensedHistory)

#         with xlsxwriter.Workbook(filename) as workbook:
#             if worksheet is None:
#                 sheet_name = self.comp.name[:31]
#                 worksheet = workbook.add_worksheet(sheet_name)

#             # Time steps
#             worksheet.write(0, 0, "Time Step")
#             worksheet.write_column(1, 0, np.arange(num_steps))

#             # True states
#             worksheet.write(0, 1, "Comp Truth State")
#             worksheet.write_column(1, 1, self.comp.history)

#             # Sensor states
#             for j, sensor in enumerate(self.sensors):
#                 worksheet.write(0, j+2, f"Sensor {j+1} State")
#                 worksheet.write_column(1, j+2, sensor.history)

#             # Sensed aggregated states
#             col_offset = len(self.sensors) + 2
#             worksheet.write(0, col_offset, "Comp Sensed State")
#             worksheet.write_column(1, col_offset, self.sensedHistory)
#             for j, sensor in enumerate(self.sensors):
#                 worksheet.write(0, col_offset + j + 1, f"Sensor {j+1} Reading")
#                 worksheet.write_column(1, col_offset + j + 1, sensor.sensedHistory)

#             # Add formulas for performance
#             truth_col = 1
#             sensed_col = col_offset
#             f1_col = sensed_col + len(self.sensors) + 1
#             f2_col = f1_col + 1
#             for i in range(num_steps):
#                 addUnsensedFailureFormula(workbook, worksheet, i, truth_col, sensed_col, f1_col, num_steps)
#                 addSensorFailureFormula(workbook, worksheet, i, truth_col, f2_col, num_steps, len(self.sensors))

#             finalFormatting(worksheet, 1)

#     # ---------------------- Summary of Readings ---------------------------
#     def summaryOfReadings(self):
#         """Vectorized computation of sensor reading errors compared to true component state."""
#         comp_history = np.array(self.comp.history)
#         sensed_history = np.array(self.sensedHistory)
#         n_sensors = len(self.sensors)

#         SM_counts = np.array([np.sum(np.array(sensor.sensedHistory) != comp_history) for sensor in self.sensors])
#         FN_counts = np.array([np.sum((np.array(sensor.sensedHistory) == 0) & (comp_history == 2)) for sensor in self.sensors])
#         FP_counts = np.array([np.sum((np.array(sensor.sensedHistory) == 2) & (comp_history == 0)) for sensor in self.sensors])
#         FA_counts = np.array([np.sum((np.array(sensor.sensedHistory) == 1) & (comp_history == 2)) for sensor in self.sensors])
#         MA_counts = np.array([np.sum((np.array(sensor.sensedHistory) == 2) & (comp_history == 1)) for sensor in self.sensors])

#         SM_aggregate = np.sum(sensed_history != comp_history)
#         FN_aggregate = np.sum((sensed_history == 0) & (comp_history == 2))
#         FP_aggregate = np.sum((sensed_history == 2) & (comp_history == 0))
#         FA_aggregate = np.sum((sensed_history == 1) & (comp_history == 2))
#         MA_aggregate = np.sum((sensed_history == 2) & (comp_history == 1))

#         headers = ["Sensor", "SM", "FN", "FP", "FA", "MA"]
#         rows = zip(range(1, n_sensors + 1), SM_counts, FN_counts, FP_counts, FA_counts, MA_counts)
#         aggregate_row = ["Aggregate", SM_aggregate, FN_aggregate, FP_aggregate, FA_aggregate, MA_aggregate]

#         print(tabulate([headers] + list(rows) + [aggregate_row], headers="firstrow"))





import numpy as np
from shipClass.Component import Component
from shipClass.Sensor_basic import Sensor


class SensedComp:
    """
    A component with attached sensors that produce sensed states based on detection probabilities.
    """

    def __init__(self, comp: Component, sensors: list[Sensor]):
        self.comp = comp
        self.sensors = sensors
        self.history = np.array([], dtype=int)
        self.sensedHistory = np.array([], dtype=int)

    def attach_sensors(self):
        """Attach sensors to this component."""
        for s in self.sensors:
            s.attachedComp = self

    def reset(self):
        """Reset the component and its sensors."""
        self.comp.reset()
        self.history = np.array([], dtype=int)
        self.sensedHistory = np.array([], dtype=int)
        for s in self.sensors:
            s.reset()
    def simulate(self, num_steps=1, debug=False):
        """
        Simulate component behavior and its sensed states.

        Parameters
        ----------
        num_steps : int
            Number of time steps to simulate.
        debug : bool
            If True, print summary of sensor vs truth agreement.
        """
        # --- Simulate the true component behavior ---
        self.comp.simulate(num_steps)
        truth_history = self.comp.history[-num_steps:]  # shape (num_steps,)

        if len(self.sensors) == 0:
            raise ValueError("SensedComp.simulate: No sensors attached to component.")

        # --- Each sensor reads the true states (updates its own sensedHistory) ---
        for sensor in self.sensors:
            sensor.read(truth_history)  # updates sensor.sensedHistory internally

        # --- Stack the last num_steps from each sensor ---
        all_sensor_readings = np.vstack([
            sensor.sensedHistory[-num_steps:] for sensor in self.sensors
        ])  # shape: (num_sensors, num_steps)

        n_states = len(self.sensors[0].observation_probs)

        # --- Majority vote (vectorized) ---
        one_hot = np.eye(n_states, dtype=int)[all_sensor_readings]  # (num_sensors, num_steps, n_states)
        counts = one_hot.sum(axis=0)                                # (num_steps, n_states)
        eps = np.linspace(0, 1e-9, n_states)                        # tiny bias for deterministic ties
        sensed_readings = (counts + eps).argmax(axis=1)              # (num_steps,)

        # --- Store combined sensed history for the component ---
        self.sensedHistory = np.concatenate([self.sensedHistory, sensed_readings])

    # # --- Optional debugging info ---
    # if debug:
    #     acc = np.mean(sensed_readings == truth_history)
    #     unique, counts_true = np.unique(truth_history, return_counts=True)
    #     print(f"[DEBUG] SensedComp: accuracy={acc:.3f}, truth dist={dict(zip(unique, counts_true))}")

    # return self.sensedHistory

    # ---------------------- Plotting Functions -----------------------------
    def plotHistory(self):
        ax = self.comp.plotHistory()
        for sensor in self.sensors:
            sensor.plotReadings(ax)
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.show()

    def confusionMatrix(self):
        """Compute confusion matrix between true component states and sensed states."""
        from sklearn.metrics import confusion_matrix
        import seaborn as sns

        # plot the confusion matrix
        labels = ['failed', 'alarm', 'working']  # 0=Fail, 1=Alarm, 2=Working
        cm = confusion_matrix(self.comp.history[-len(self.sensedHistory):], self.sensedHistory, labels=[0, 1, 2])
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
        plt.xlabel("Sensed")
        plt.ylabel("True")
        plt.title(f"Confusion Matrix - Sensor Quality: {self.sensors[0].quality}")
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
