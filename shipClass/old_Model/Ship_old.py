""" 
This class is used to create a ship object (parent class). 
Different types of ships (manned and unmanned) will inherit from this class.
"""

from shipClass.old_Model.System_old import System
from shipClass.SensedComp import SensedComp
from shipClass.SeriesComps import SeriesSensedComps
from shipClass.Component import Component
from utils.helperFunctions import SolveStructureFunction
from utils.excelFunctions import addTimeSteps, addTruth, addSensed, addUnsensedFailureFormula, highlightParallels, finalFormatting

import matplotlib.pyplot as plt
import pandas as pd
import xlsxwriter
import ast

class Ship:

    def __init__(self, name, excel_file):
        self.name = name
        self.ship_data_file= excel_file
        self.systems = self.initializeShipSystemsfromExcel()

# ---------------------------Useful Functions ---------------------------
    def print_comp_names(self, system_name = None):
        if system_name is None:
            for sys_name, sys in self.systems.items():
                print(f"System: {sys_name}")
                for comp in sys.comps:
                    print(f"  Component {comp.name}")
        else:
            sys = self.systems.get(system_name)
            if sys:
                print(f"System: {system_name}")
                for comp in sys.comps:
                    print(f"  Component {comp.name}")

# ------------------------------- Initialization ------------------------
    def initializeShipSystemsfromExcel(self, unmanned: bool = False):

        # read in data from excel file
        excel_file = self.ship_data_file    
        rel_df= pd.read_excel(excel_file, sheet_name = 'machinery reliability data')
        sys_structure_df = pd.read_excel(excel_file, sheet_name='system structure data')
        sys_structure_df['Structure']= sys_structure_df['Structure'].apply(ast.literal_eval) # convert structure description from str to list
        # go through each system and set it up according to the given structure
        ship_systems = {}
        sys_parallels = []
        for i, sys_struct in enumerate(sys_structure_df.Structure):
            # sys_struct = ast.literal_eval(sys_struct) # convert structure description from str to list
            
            sys_comps = []

            for comp in sys_struct:

                # single component in series, added easily
                if type(comp) is int:

                    # intialize it as a SensedComp
                    comp_name = rel_df.Component[comp]
                    comp_MTTF = rel_df.MTBF[comp]
                    comp_MTTR = rel_df.MTTR[comp]
                    sensed_comp = SensedComp(Component(comp_name, comp_MTTF, comp_MTTR))

                    # add it directly to the dictionary of system comps
                    sys_comps.append( sensed_comp )

                # if tuple, component is in a parallel set, add it to the systems list of parallels before adding it to the system
                elif type(comp) is tuple:
                    parallel_set = list(comp)
                    print(f'Parallel set: {parallel_set}')

                    # add the individual comps from the parallel sets to the system
                    for j,idx in enumerate(parallel_set):
                        
                        # if the index in the tuple is an int, it is a single component
                        if type(idx) is int: 
                            comp_name = rel_df.Component[idx]
                            comp_MTTF = rel_df.MTBF[idx]
                            comp_MTTR = rel_df.MTTR[idx]
                            sensed_comp = SensedComp(Component(comp_name, comp_MTTF, comp_MTTR))
                            
                            # add it directly to the dictionary of system comps
                            sys_comps.append( sensed_comp)
                            parallel_set[j] = sensed_comp 
                    
                        
                        #if the index in the tuple is a list, it is a group of series components
                        elif type(idx) is list: 
                            series_set = idx
                            series_set_comps = []
                            print(series_set)

                            for k,idx in enumerate(series_set):

                                if type(idx) is int: # if the index is an int, it is a single component
                                    comp_name = rel_df.Component[idx]
                                    comp_MTTF = rel_df.MTBF[idx]
                                    comp_MTTR = rel_df.MTTR[idx]
                                    sensed_comp = SensedComp(Component(comp_name, comp_MTTF, comp_MTTR))
                                    series_set_comps.append( sensed_comp )  # add the sensed component to the series set
                                
                            # define the series set as a seriesSensedComp
                            series_set = SeriesSensedComps(components=series_set_comps)
                            sys_comps.append( series_set )
                            parallel_set[j] = series_set
                   
                    # replace parallel_set with their locations within the system
                    parallel_set = tuple([sys_comps.index(comp)+1 for comp in parallel_set])
                    sys_parallels.append(parallel_set) # add the index of the parallel set to the list of parallels for the system     

            # add the system components to a system object
            sys_name = sys_structure_df.System[i]
            if sys_parallels == []:
                ship_systems[sys_name] = System(sys_name, sys_comps, unmanned=unmanned)  
            else: 
                print(sys_parallels)
                ship_systems[sys_name] = System(sys_name, sys_comps, sys_parallels, unmanned=unmanned)  

        return ship_systems

# ------------------------- Simulation Functions ----------------------     

    def simulate(self, num_hours: int) -> None: 
        '''
        This method simulates the ship object by iterating through each system and performing maintenance actions as needed.
        '''
        
        # Iterate through each system and update it, then perform maintenance actions as needed
        for hours in range(num_hours): 
        
            # Update the state of all the systems
            for system in self.systems:
                if len(system.history) <= len(self.history): # checks that the system didnt experience a maintenance action
                    system.simulate(1)
                    
            # Determine and store the sensed state of the ship
            self.sensedState = SolveStructureFunction(self.systems, self.parallels)
            self.sensedHistory.append(self.sensedState)

            # Determine and store the true state of the ship
            self.state = SolveStructureFunction(self.systems, self.parallels, True)
            self.history.append(self.state)


# ------------------------- Plotting Functions ----------------------     
        
    def plotHistory(self) -> None:
        """
        This method plots the history of the ship's state and sensed state over time.
        """
        # create a new figure
        fig, ax = plt.subplots()

    
        ax.plot(self.history, label='True State')
        ax.plot(self.sensedHistory, label='Sensed State')

        # formatting the plot        
        ax.set_title(f'{self.name} State History')
        # ax.xticks(range(len(self.history)), [f'{i}h' for i in range(len(self.history))], rotation=45) # make x ticks for every hour
        ax.set_xticks(range(0, len(self.history), 5), [f'{i}h' for i in range(0, len(self.history), 5)], rotation=45)   # make x ticks for every 5 hours
        ax.set_xlim(0, len(self.history))
        ax.set_xlabel('Time (hours)')
        ax.set_yticks(list(self.states.keys()))  
        ax.set_yticklabels(list(self.states.values()))
        ax.set_ylabel('State')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                  fancybox=True, shadow=True, ncol=5)
        ax.grid()        
        plt.show()



    def printHistory2Excel(self, filename: str, worksheet= None) -> None:
        """ Print the history of the ship and its systems to an excel file """

        # # create the headers for the ship history sheet
        # ship_truth_headers = [f'Ship Truth'] + [f'System {i+1} Truth' for i in range(self.n)]
        # ship_sensed_headers = [f'Ship Sensed'] + [f'System {i+1} Sensed' for i in range(self.n)]
        # headers = ['Time'] + ship_truth_headers + ship_sensed_headers
        
        # determine the columns for adding formulas to the sheet
        truth_col = 2
        sensed_col = 2 + self.n + 1
        f1_col = 2 + self.n + 1 + self.n + 1

        # add to the workbook using xlsxwriter
        with xlsxwriter.Workbook(filename) as workbook:
            
            # if no worksheet is provided, create a new workbook and worksheet
            if worksheet is None:
                worksheet = workbook.add_worksheet(self.name) 
            
            # add data to the worksheet
            num_data = len(self.history)
            for i in range(num_data):

                # add the time steps to the first column
                addTimeSteps(workbook, worksheet,i)

                # add truth data from the ship and its systems
                truth_data = [self.history[i]] + [self.systems[j].history[i] for j in range(self.n)] 
                if i==0:
                    ship_truth_headers = [f'Ship Truth State'] + [f'System {i+1} Truth State' for i in range(self.n)]
                    addTruth(workbook, worksheet, i, truth_data, ship_truth_headers)
                else: 
                    addTruth(workbook, worksheet, i, truth_data)

            
                sensed_data = [self.sensedHistory[i]] + [self.systems[j].sensedHistory[i] for j in range(self.n)]
                if i ==0:
                    ship_sensed_headers = [f'Ship Sensed State'] + [f'System {i+1} Sensed State' for i in range(self.n)]
                    addSensed(workbook, worksheet, i, sensed_data, ship_sensed_headers)
                else:
                    addSensed(workbook, worksheet, i, sensed_data)
                    
                # add formula for checking if the sensed state matches the truth state
                addUnsensedFailureFormula(workbook, worksheet, i, truth_col, sensed_col, f1_col, num_data)

            # add formating for parallel components
            if self.parallels is not None:
                highlightParallels(workbook, worksheet, self.parallels, num_data, self.n)
            
            # finalFormatting(worksheet, self.n)       

            # add each systems data to their own worksheet
            for i in range(self.n):
                # create a new worksheet for each system
                ws = workbook.add_worksheet(f'System {i+1} History')

                # add the history of the system to the worksheet
                self.systems[i].printHistory2Excel(filename, ws, False)

