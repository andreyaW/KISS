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
        self.sensedState = SolveStructureFunction(self.sensedComps, self.system.parallels, sensed=True)[-1]
        self.sensedHistory = np.array([self.sensedState])  # initialize with initial sensed state

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
        self.system.history = np.concatenate([self.system.history, SolveStructureFunction(self.system.comps, self.system.parallels, time_steps)])
        self.system.state = self.system.history[-1]
        
        # solve the system structure function to get the sensed state of the system
        self.sensedHistory = np.concatenate([self.sensedHistory, SolveStructureFunction(self.sensedComps, self.system.parallels, time_steps, sensed=True)])
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
        
#     def printHistory2Excel(self, filename: str = 'system_history.xlsx',  worksheet=None, addComps:bool = False) -> None:
#         """ Print the history of the system and its sensed components to an excel file """

#         # determine important column letter numbers
#         truth_col =2
#         sensed_col = 3 + self.system.n
#         f1_col = 4 + self.system.n*2

#         self.system.check4DuplicateNames()  # check for duplicate component names and update them to be unique

#         # add to the workbook using xlsxwriter
#         with xlsxwriter.Workbook(filename) as workbook:

#             # if no worksheet is provided, create a new workbook and worksheet
#             if worksheet is None:
#                 if len(self.system.name) > 31:
#                     sheet_name = self.system.name[:31]
#                 else: 
#                     sheet_name = self.system.name
#                 worksheet = workbook.add_worksheet(sheet_name)

#             # add data to the sheet
#             num_data = len(self.sensedHistory)
#             for i in range(num_data):
                
#                 # add the time steps to the first column
#                 addTimeSteps(workbook, worksheet, i)

#                 # add truth states of the system and each sensed component to the row
#                 sys_truth = [self.system.history[i]]
#                 comps_truth = []
#                 for comps in range(self.system.n):
#                     if isinstance(self.sensedComps[comps], SensedSystem):
#                         comps_truth.append(self.sensedComps[comps].system.history[i])
#                     else:
#                         comps_truth.append(self.sensedComps[comps].comp.history[i])
#                 truth_data = sys_truth + comps_truth
#                 if i == 0:
#                     sys_truth_headers = ['Sys Truth State'] + [comp.name.capitalize() + ' Truth State' for comp in self.system.comps]
#                     addTruth(workbook, worksheet, i, truth_data, sys_truth_headers)
#                 else:
#                     addTruth(workbook, worksheet, i, truth_data)

#                 # add the sensed states of te system and each sensed component to the row
#                 sensed_data = [self.sensedHistory[i]] + [self.sensedComps[j].sensedHistory[i] for j in range(self.system.n)]
#                 if i == 0:
#                     sys_sensed_headers = ['Sys Sensed State'] + [comp.name.capitalize() + ' Sensed State' for comp in self.system.comps]
#                     addSensed(workbook, worksheet, i, sensed_data, sys_sensed_headers)
#                 else:
#                     addSensed(workbook, worksheet, i, sensed_data)

#                 # add formula for checking if the sensed state matches the truth state
#                 addUnsensedFailureFormula(workbook, worksheet, i, truth_col, sensed_col, f1_col, num_data)

#             # add formating for parallel components
#             if self.system.parallels is not None:
#                 highlightParallels(workbook, worksheet, self.system.parallels, num_data, self.system.n)
            
#             finalFormatting(worksheet, self.system.n)

#             # add each sensed componet to its own worksheet
#             if addComps:
#                 for comp in self.sensedComps:

#                     if type(comp) is SensedComp:
#                         # create a new worksheet for each component in the system (comp or seriesComps)
#                         comp_name = comp.comp.name.capitalize()
#                         ws= workbook.add_worksheet(comp_name)

#                         # add the history of the component to the worksheet
#                         comp.printHistory2Excel(filename, worksheet=ws)

#                     else: 
#                         sub_sys= comp  # sensed subsystem
#                         # create a new worksheet for each subsystem in the system (comp or seriesComps)
#                         sub_sys_name = sub_sys.system.name.capitalize()
#                         ws= workbook.add_worksheet(sub_sys_name)

#                         # add the history of the subsystem to the worksheet
#                         sub_sys.printHistory2Excel(filename, worksheet=ws)

#                         # for the seriesComps object, add each component to its own worksheet
#                         for sub_comp in sub_sys.sensedComps:
#                             comp_name = sub_comp.comp.name.capitalize()
#                             ws= workbook.add_worksheet(comp_name)

#                             # add the history of the component to the worksheet
#                             sub_comp.printHistory2Excel(filename, worksheet=ws)

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
