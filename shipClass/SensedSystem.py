from shipClass.System import System
from shipClass.Sensor_basic import Sensor
from shipClass.SensedComp import SensedComp
from utils.helperFunctions import SolveStructureFunction
from utils.excelFunctions import addTimeSteps, addTruth, addSensed, addUnsensedFailureFormula, highlightParallels, finalFormatting

import matplotlib.pyplot as plt
import xlsxwriter
import numpy as np

class SensedSystem():
    ''' a class which holds the system class and also attaches sensors to each component of the system to get readings '''
    
    def __init__(self, system: System, sensors: list[tuple[int, str]] = None):
        self.system = system        
        self.sensedComps = []
        self.sensors = sensors
        self.attach_sensors()
        self.sensedState = self.system.state  # initialize sensed state to true state
        self.sensedHistory = np.array([self.sensedState]) 

    def attach_sensors(self):
        # if the sensors are not specified, add defaults
        if self.sensors is None:
            self.sensors = [[(3, 'Good') for comps in self.sensedComps]]

        comps = self.system.comps
        for i, comp in enumerate(comps):
            if isinstance(comp, System):
                # if the component is a subsystem, recursively attach sensors to its components
                sub_sys_sensors = [self.sensors[i] for _ in comp.comps]
                sensed_subsystem = SensedSystem(comp, sensors=sub_sys_sensors)
                self.sensedComps.append(sensed_subsystem)
                continue
            else: 
                # if the component is a individual component, attach the designated quality and number of sensors to it
                sensors = [Sensor(quality=self.sensors[i][1]) for _ in range(self.sensors[i][0])]
                sensed_comp = SensedComp(comp, sensors)
                self.sensedComps.append(sensed_comp)

    def simulate(self, time_steps=1):
        ''' simulate the system and all its sensed components for a number of time steps '''
        # simulate the sensed components of the system (updates history and sensedHistory)
        for sc in self.sensedComps:
            sc.simulate(time_steps)

        # solve the system structure function to get the true state of the system
        true_history = SolveStructureFunction([sc.comp for sc in self.sensedComps], self.system.parallels, time_steps)
        self.system.history = np.concatenate([self.system.history, true_history])
        self.system.state = self.system.history[-1]
        
        # solve the system structure function to get the sensed state of the system
        sensed_history = SolveStructureFunction(self.sensedComps, self.system.parallels, time_steps, sensed=True)
        self.sensedHistory = np.concatenate([self.sensedHistory, sensed_history])
        self.sensedState = self.sensedHistory[-1]

    def reset(self):
        # reset each sensed component of the system
        for sensed_comp in self.sensedComps:
            sensed_comp.reset()

        # reset the history of the true system (assume initial system state (all components operational))
        self.system.state = max(self.system.states.keys())
        self.system.history = np.array([self.system.state], dtype=int)

        # reset the sensed history of the system (assume initial sensed state is correct)
        self.sensedState = self.system.state
        self.sensedHistory = np.array([self.sensedState], dtype=int)

    def plotHistory(self, plot_comp_history = False, return_ax = False):
        ''' plot the history of the sensed system '''
        # plot the true history of the system
        ax = self.system.plotHistory(plot_comp_history, return_ax=True)

        # plot the sensed history of the system
        ax.plot(self.sensedHistory, marker=',', label='Sensed', 
                linestyle='--', color='orange')

        # add updated legend
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                fancybox=True, shadow=True, ncol=5)
        plt.show()

        if return_ax:
            return ax
        
    def printHistory2Excel(self, filename: str = 'system_history.xlsx',
                           worksheet=None, addComps: bool = False) -> None:
        """Vectorized Excel export of the system and its sensed components."""

        self.system.check4DuplicateNames()
        num_steps = len(self.sensedHistory)

        with xlsxwriter.Workbook(filename) as workbook:
            # main worksheet
            if worksheet is None:
                sheet_name = self.system.name[:31]
                worksheet = workbook.add_worksheet(sheet_name)

            # time steps
            worksheet.write(0, 0, "Time Step")
            worksheet.write_column(1, 0, np.arange(num_steps))

            # system truth
            worksheet.write(0, 1, "System Truth State")
            worksheet.write_column(1, 1, self.system.history)

            # component truth
            for j, comp in enumerate(self.system.comps):
                worksheet.write(0, j+2, f"{comp.name.capitalize()} Truth State")
                worksheet.write_column(1, j+2, comp.history)

            # system sensed
            col_offset = self.system.n + 2
            worksheet.write(0, col_offset, "System Sensed State")
            worksheet.write_column(1, col_offset, self.sensedHistory)

            # component sensed
            for j, sensed_comp in enumerate(self.sensedComps):
                worksheet.write(0, col_offset + j + 1,
                                f"{self.system.comps[j].name.capitalize()} Sensed State")
                worksheet.write_column(1, col_offset + j + 1, sensed_comp.sensedHistory)

            # parallel highlighting & formatting
            if self.system.parallels is not None:
                highlightParallels(workbook, worksheet, self.system.parallels,
                                   num_steps, self.system.n)
            finalFormatting(worksheet, self.system.n)

            # optional: per-component worksheets
            if addComps:
                for sensed_comp in self.sensedComps:
                    ws = workbook.add_worksheet(sensed_comp.comp.name[:31])
                    sensed_comp.printHistory2Excel(filename, worksheet=ws)
