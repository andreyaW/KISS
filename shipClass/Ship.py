from shipClass.System import System
from shipClass.SeriesComps import SeriesComps
from shipClass.Component import Component
from utils.helperFunctions import SolveStructureFunction, set_x_ticks
from utils.excelFunctions import addTruth, addTimeSteps, highlightParallels, finalFormatting

import matplotlib.pyplot as plt
import pandas as pd
import xlsxwriter
import ast

class Ship:

    def __init__(self, name, excel_file, repairable: bool):
        self.name = name
        self.initializeShipSystemsfromExcel(excel_file, repairable)

    def initializeShipSystemsfromExcel(self, excel_file, repairable: bool):

        # read in data from excel file
        # excel_file = self.ship_data_file    
        rel_df= pd.read_excel(excel_file, sheet_name = 0) #read in machinery reliability data from first sheet
        sys_structure_df = pd.read_excel(excel_file, sheet_name=1) # read in system structure data from second sheet
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
                    comp = Component(comp_name, comp_MTTF, comp_MTTR)

                    # add it directly to the dictionary of system comps
                    sys_comps.append( comp )

                # if tuple, component is in a parallel set, add it to the systems list of parallels before adding it to the system
                elif type(comp) is tuple:
                    parallel_set = list(comp)

                    # add the individual comps from the parallel sets to the system
                    for j,idx in enumerate(parallel_set):
                        
                        # if the index in the tuple is an int, it is a single component
                        if type(idx) is int: 
                            comp_name = rel_df.Component[idx]
                            comp_MTTF = rel_df.MTBF[idx]
                            comp_MTTR = rel_df.MTTR[idx]
                            comp = Component(comp_name, comp_MTTF, comp_MTTR)
                            
                            # add it directly to the dictionary of system comps
                            sys_comps.append( comp)
                            parallel_set[j] = comp 
                        
                        #if the index in the tuple is a list, it is a group of series components
                        elif type(idx) is list: 
                            series_set = idx
                            series_set_comps = []

                            for k,idx in enumerate(series_set):

                                if type(idx) is int: # if the index is an int, it is a single component
                                    comp_name = rel_df.Component[idx]
                                    comp_MTTF = rel_df.MTBF[idx]
                                    comp_MTTR = rel_df.MTTR[idx]
                                    comp = Component(comp_name, comp_MTTF, comp_MTTR)
                                    series_set_comps.append( comp )  # add the sensed component to the series set
                                
                            # define the series set as a seriesSensedComp
                            series_set = SeriesComps(components=series_set_comps)
                            sys_comps.append( series_set )
                            parallel_set[j] = series_set
                   
                    # replace parallel_set with their locations within the system
                    parallel_set = tuple([sys_comps.index(comp)+1 for comp in parallel_set])
                    sys_parallels.append(parallel_set) # add the index of the parallel set to the list of parallels for the system     

            # add the system components to a system object
            sys_name = sys_structure_df.System[i]
            if sys_parallels == []:
                ship_systems[sys_name] = System(sys_name, sys_comps, repairable=repairable)  
            else: 
                ship_systems[sys_name] = System(sys_name, sys_comps, sys_parallels, repairable=repairable)  
        
        # setting necessary ship parameters
        self.systems = ship_systems
        self.n = len(self.systems)  # number of total systems in the ship
        self.parallels = []
        self.states = ship_systems[sys_name].states  # Assuming all systems have the same states
        self.state = max(self.states.keys())
        self.history = [self.state]

# ------------ Simulation Functions -------------------
    def simulate(self, num_steps):
        systems = list(self.systems.values())
        for _ in range(num_steps):
            for sys in systems:
                sys.simulate(1)
            self.state = SolveStructureFunction(systems, self.parallels)  
            self.history.append(self.state)

# ------------ Plotting Functions -------------------
    def plotHistory(self, show=True):

        # Create a figure and axis
        fig, ax = plt.subplots()
        
        # Plot the true and sensed history of the system
        ax.plot(self.history, marker=',', label='Truth')

        # Formatting
        ax.set_ylabel('State')
        ax.set_yticks(list(self.states.keys()))         # y ticks are labeled with the state names
        ax.set_yticklabels(list(self.states.values()))
        ax.set_xlabel('Time Step')
        set_x_ticks(ax, len(self.history))              # function which sets x limits based on len(history)
        ax.grid()
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  fancybox=True, shadow=True, ncol=5)

# ------------ Excel Functions --------------------
    def printHistory2Excel(self, filename: str, worksheet= None) -> None:
        """ Print the history of the ship and its systems to an excel file """

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

            # add formating for parallel components
            if self.parallels is not None:
                highlightParallels(workbook, worksheet, self.parallels, num_data, self.n)
            
            finalFormatting(worksheet, self.n)       

            # add each systems data to their own worksheet
            for i in range(self.n):
                # create a new worksheet for each system
                ws = workbook.add_worksheet(f'System {i+1} History')

                # add the history of the system to the worksheet
                self.systems[i].printHistory2Excel(filename, ws, False)
