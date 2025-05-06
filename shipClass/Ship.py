""" 
This class is used to create a ship object (parent class). 
Different types of ships (manned and unmanned) will inherit from this class.
"""

from shipClass.System import System
from utils.helperFunctions import SolveStructureFunction, idx2letter

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


    def printHistory2Excel(self, filename: str) -> None:
        """ Print the history of the ship and its systems to an excel file """

        # create the headers for the ship history sheet
        ship_truth_headers = [f'Ship Truth'] + [f'System {i+1} Truth' for i in range(self.n)]
        ship_sensed_headers = [f'Ship Sensed'] + [f'System {i+1} Sensed' for i in range(self.n)]
        headers = ['Time'] + ship_truth_headers + ship_sensed_headers
        
        # determine the columns for adding formulas to the sheet
        truth_col = idx2letter(2)
        sensed_col = idx2letter(2 + self.n + 1) 
        f1_col = idx2letter(2 + self.n + 1 + self.n + 1)

        # Create a new Excel file 
        with xlsxwriter.Workbook(filename) as workbook:
            
            # Create a new worksheet for the ship history
            worksheet = workbook.add_worksheet('Ship')
            
            # write the headers in the first row
            cell_format = workbook.add_format()            
            cell_format.set_text_wrap()             # wrap text header row
            worksheet.write_row(0, 0, headers, cell_format)

            # add the ship history to the sheet
            for i in range(len(self.history)):
                
                true_history = [self.history[i]] + [self.systems[j].history[i] for j in range(self.n)]
                sensed_history = [self.sensedHistory[i]] + [self.systems[j].sensedHistory[i] for j in range(self.n)]
                data = [i] + true_history + sensed_history
                worksheet.write_row(i+1, 0, data)
                
                # add the formulas to the sheet
                row = i + 2
                f1=f"IF({truth_col}{row}={sensed_col}{row},1,0)" 
                worksheet.write_formula(f"{f1_col}{row}", f1)

            # add conditional formatting to formula colums
            worksheet.conditional_format(f'{f1_col}2:{f1_col}{row}', 
                                           {'type': '2_color_scale',
                                            'min_color': '#FD0000',  # red
                                            'max_color': '#00FD00'}) # green

            # increase the column width for better readability
            worksheet.set_column(0, 0, 20)

            # add the systems data to new sheets
            for i in range(self.n):
                worksheet = workbook.add_worksheet(f'System {i+1}')
                self.systems[i].printHistory2Excel(filename, worksheet)
