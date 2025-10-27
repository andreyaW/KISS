from shipClass.Component import Component
from shipClass.Sensor_basic import Sensor
from utils.helperFunctions import find_mode
from tabulate import tabulate
from utils.excelFunctions import addUnsensedFailureFormula, addSensorFailureFormula, finalFormatting

import xlsxwriter
import matplotlib.pyplot as plt
import numpy as np

class SensedComp:
    """
    A component with attached sensors that produce sensed states based on detection probabilities.
    """

    def __init__(self, comp: Component, sensors: list[Sensor]):
        self.comp = comp
        self.sensors = sensors
        self.sensedHistory = np.array([self.comp.state], dtype=int)

    def attach_sensors(self):
        """Attach sensors to this component."""
        for s in self.sensors:
            s.attachedComp = self

    def reset(self):
        """Reset the component and its sensors."""
        self.comp.reset()
        for s in self.sensors:
            s.reset()
        self.sensedHistory = np.array([self.comp.state], dtype=int)


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

        # # USE HMM MULTI-SENSOR FILTERING APPROACH
        # sensed_readings = self.hmm_multisensor_filter(truth_history)

        # --- USE MAJORITY VOTE APPROACH ---
        sensed_readings = self.majority_vote(truth_history)

        # --- Store combined sensed history for the component ---
        self.sensedHistory = np.concatenate([self.sensedHistory, sensed_readings])

    def majority_vote(self, truth_history):
        """ simulate sensor readings and aggregate them using majority vote """
        # --- Each sensor reads the true states (updates its own sensedHistory) ---
        num_steps = len(truth_history)
        
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
        sensed_readings = (counts + eps).argmax(axis=1)             # (num_steps,)
        return sensed_readings
    

    def hmm_multisensor_filter(self, truth_history):
        P = self.comp.transition_matrix                                 # Transition matrix from the component
        O_list = [sensor.observation_probs for sensor in self.sensors]  # List of observation matrices from each sensor

        n_states = P.shape[0]
        n_sensors = len(self.sensors)
        n_steps = len(truth_history)
        T = len(truth_history)
        belief = np.zeros(n_states)

        # --- Simulate multi-sensor readings ---
        sensor_readings = np.zeros((n_steps, n_sensors), dtype=int)
        for t in range(n_steps):
            for i in range(n_sensors):
                sensor_readings[t, i] = np.random.choice([0, 1, 2], p=O_list[i][truth_history[t]])

        # --- update beliefs over time ---
        init_state = truth_history[0]
        belief[init_state] = 1.0    # start fully Healthy with 100% certainty
        beliefs = np.zeros((T, n_states))
        for t in range(T):
            # Predict step
            belief = belief @ P      # spread belief based on transition probabilities 
            # Update step — multiply all sensor likelihoods
            obs = sensor_readings[t]
            likelihood = np.ones(n_states)
            for i, O in enumerate(O_list):
                likelihood *= O[:, obs[i]]
            belief *= likelihood
            # Normalize
            belief /= belief.sum()
            beliefs[t] = belief
        
        # --- Get estimated states from beliefs ---
        estimated_states = beliefs.argmax(axis=1) 
        return estimated_states

    # ---------------------- Plotting Functions -----------------------------
    def plotHistory(self, showPlot: bool = True, ax=None):
        """Plot the history of the component and its sensors."""
        if ax is None:
            ax = self.comp.plotHistory()
        else: 
            self.comp.plotHistory(ax=ax)
        
        for sensor in self.sensors:
            sensor.plotReadings(ax)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=len(self.sensors) + 1) # add legend below plot
        ax.set_title(f"Sensed Component History - {self.comp.name} with {len(self.sensors)} Sensors")

        if showPlot:
            plt.show()

        return ax     

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

    def printSensorMatrix(self):
        """ Print the number of sensors and each sensor matrix for the sensors attached to this component. """
        print(f"Component: {self.comp.name}")
        print(f"Number of Sensors: {len(self.sensors)}")
        for i, sensor in enumerate(self.sensors):
            print(f"Sensor {i+1} (Quality: {sensor.quality}):")
            print(sensor.observation_probs)
            print()


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
            truth_col = 2
            sensed_col = col_offset
            f1_col = sensed_col + len(self.sensors) + 1
            f2_col = f1_col + 1

            addSensorFailureFormula(workbook, worksheet, truth_col, f2_col, num_steps, len(self.sensors))
            addUnsensedFailureFormula(workbook, worksheet, truth_col, sensed_col, f1_col, num_steps)
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
