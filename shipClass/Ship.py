""" 
This class is used to create a ship object (parent class). 
Different types of ships (manned and unmanned) will inherit from this class.
"""

from shipClass.System import System
from utils.helperFunctions import SolveStructureFunction
from utils.excelFunctions import addTimeSteps, addTruth, addSensed, addUnsensedFailureFormula, highlightParallels, finalFormatting

import matplotlib.pyplot as plt
import xlsxwriter

class Ship:

    def __init__(self, name, systems: list[System], parallels=None) -> None:
        '''
        param systems: A list of System objects representing the systems on the ship.
        '''
        self.name = name
        self.systems = systems
        self.parallels = parallels
        self.n = len(self.systems)
        self.nPar = len(parallels) if parallels is not None else 0
        self.states = self.systems[0].states  # states of the ship (same as the states of the systems)

        self.sensedState = SolveStructureFunction(self.systems, parallels)  # sensed state of the ship
        self.sensedHistory = [self.sensedState]
        self.extendedSensedHistory = self.sensedHistory

        self.state = SolveStructureFunction(self.systems, parallels, True)  # true state of the ship
        self.history = [self.state]
        self.extendedHistory = self.history

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
            # if self.parallels is not None:
            #     highlightParallels(workbook, worksheet, self.parallels, num_data, self.n)
            
            finalFormatting(worksheet, self.n)       

            # add each systems data to their own worksheet
            for i in range(self.n):
                worksheet = workbook.add_worksheet(f'System {i+1} History')
                self.systems[i].printHistory2Excel(filename, worksheet, False)
