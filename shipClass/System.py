from shipClass.SensedComp import SensedComp
from utils.helperFunctions import SolveStructureFunction, idx2letter

import matplotlib.pyplot as plt
import xlsxwriter


class System():
    ''' a simple model of a system composed of many sensed components'''

    def __init__(self, name, comps: list[SensedComp], parallels = None)-> None:
        self.name = name
        self.comps = comps
        self.parallels = parallels
        self.states = self.comps[0].comp.states
        self.n = len(self.comps)                                         # number of total components in the system
        self.nPar = len(self.parallels) if parallels is not None else 0  # number of parallel components in the system
                
        # true state of the system
        self.state = SolveStructureFunction(self.comps, self.parallels)  
        self.history = [self.state]  
        
        # sensed state of the system
        self.sensedState = SolveStructureFunction(self.comps, self.parallels)  
        self.sensedHistory = [self.sensedState]

        # extended histories of the system and its components (histories ignoring maintenance resets)
        self.extendedHistory = self.history
        self.extendedSensedHistory = self.sensedHistory  
        
# ---------------------- Simulation Functions ----------------------  
      
    def simulate(self, number_of_steps: int = 1) -> None:
        """ Simulate the system (uses simulate() from SensedComp class) """
        
        # For each step sense the state of the component
        for i in range(number_of_steps):
            
            # update the state of all the components
            for comp in self.comps:
                comp.simulate(1)
                
            # determine and store the sensed state of the system
            self.sensedState = SolveStructureFunction(self.comps, self.parallels)
            self.sensedHistory.append(self.sensedState)          
            
            # if self.sensedHistory[-1] > self.sensedHistory[-2]:  # flags when the sensed state has improved
            #     print( 'There has been an error in simulation or maintenance has occurred') # error messsage 
                
            # determine and store the true state of the system
            self.state = SolveStructureFunction(self.comps, self.parallels, True)
            self.history.append(self.state)                     # truth

    
    def reset(self):
        """ Reset the system to initial state (same objects as before, new histories) """
        
        # add previous history to extended history
        self.extendedHistory = self.extendedHistory + self.history[1:]
        self.extendedSensedHistory = self.extendedSensedHistory + self.sensedHistory[1:]

        # reset the state of all the components
        for sc in self.comps:
            sc.reset()
            
        # reset the histories of the system
        self.state = self.SolveStructureFunction(True)  
        self.history = [self.state]  
        
        self.sensedState = self.SolveStructureFunction()  
        self.sensedHistory = [self.sensedState]

    
    def failureCheck(self):
        """ Check if the system has failed """
        if self.state == 0:  # if the system is in the failed state
            return True

        # if all components are in the working state, return false
        return False   

# ---------------------- Plotting + Output Functions ----------------------  

    def outputSystemStates(self):
        ''' output the states of the system '''
        
        # Print the header
        print("{:<10} {:<5} {:<10}".format("Component", "State", "Sensed State"))
        
        # Print the states of each component
        for i, comp in enumerate(self.comps):
            print("{:<10} {:<5} {:<10}".format(comp.name, comp.state, comp.sensedState))        
        print("{:<10} {:<5} {:<10}".format(self.name, self.state, self.sensedState))        
        

    def plotHistory(self, plot_comp_history: bool = False) -> None:
        
        """ Plot the ground truth and sensed history of the system of sensed components """
            
        # Create a figure and axis
        fig, ax = plt.subplots()
        
        # Plot the true and sensed history of the system
        ax.plot(self.history, marker=',', label='Truth')
        ax.plot(self.sensedHistory, marker=',', label='Sensed')
        
        ax.set_title('Sensed System History')
        ax.set_xlabel('Time Step')
        ax.set_ylabel('State')
        ax.set_yticks(list(self.states.keys()))  
        ax.set_yticklabels(list(self.states.values()))
        ax.set_xlim(0, len(self.history))
        ax.legend()
        ax.grid()
        
        # add a marker for unsensed failures
        for i in range(len(self.history)):
            if self.history[i] != self.sensedHistory[i]:
                ax.plot(i, self.sensedHistory[i], marker='x',  color='red', markersize=10, label="Unsensed Failure")
                break
        
        plt.show()


    def printHistory2Excel(self, filename: str = 'system_history.xlsx',  worksheet=None) -> None:
        """ Print the history of the system and its sensed components to an excel file """
        
        # create and add the headers for the system history sheet
        comp_truth_headers = [f'Component {i+1} Truth' for i in range(self.n)]
        comp_sensed_headers = [f'Component {i+1} Sensed' for i in range(self.n)]
        headers = ['Time Step'] + comp_truth_headers + ['System True State'] + comp_sensed_headers + ['System Sensed State']

        # determine important column letters
        sys_truth_col = idx2letter(len(headers) - len(comp_sensed_headers) - 1)
        sys_sensed_col = idx2letter(len(headers))
        f1_col = idx2letter(len(headers) + 1)
                
        # Create a new Excel file 
        with xlsxwriter.Workbook(filename) as workbook:
            
            # if no worksheet is provided, create a new workbook and worksheet
            if worksheet is None:
                worksheet = workbook.add_worksheet(self.name) 

            # write the headers in the first row
            cell_format = workbook.add_format()            
            cell_format.set_text_wrap()             # wrap text header row
            worksheet.write_row(0, 0, headers, cell_format)

            # add data to the sheet
            for i in range(len(self.extendedHistory)):   

                # add truth and sensed states of each sensed component to the row           
                comp_truth = [self.comps[j].comp.history[i] for j in range(self.n)]
                comp_sensed = [self.comps[j].sensedHistory[i] for j in range(self.n)]
                data = [i] + [self.extendedHistory[i]] + comp_truth + [self.extendedSensedHistory[i]] + comp_sensed
                worksheet.write_row(i+1, 0, data)   # python indexes start from 0, so we need to add 1 due to header row

                # add formulas for checking results to end columns
                row = i + 2     # formulas consider data which starts from row 2
                f1 = f"IF({sys_truth_col}{row} = {sys_sensed_col}{row}, 1, 0)"
                worksheet.write_formula(f"{f1_col}{row}", f1)

            # add conditional formatting to formula colums
            worksheet.conditional_format(f'{f1_col}2:{f1_col}{row}', 
                                           {'type': '2_color_scale',
                                            'min_color': '#FD0000',  # red
                                            'max_color': '#00FD00'}) # green
            
            # increase column width for better readability
            for i in range(len(headers)):
                worksheet.set_column(i, i, 11.5)
                
            