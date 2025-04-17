from shipClass.SensedComp import SensedComp
from utils.helperFunctions import SolveStructureFunction

import matplotlib.pyplot as plt
import xlsxwriter

class System():
    ''' a simple model of a system composed of many sensed components'''

    def __init__(self, name, comps: list[SensedComp], parallels = None)-> None:
        self.name = name
        self.comps = comps
        self.parallels = parallels
        self.states = self.comps[0].comp.states
                
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
        plt.grid()
        
        # add a marker for unsensed failures
        for i in range(len(self.history)):
            if self.history[i] != self.sensedHistory[i]:
                ax.plot(i, self.sensedHistory[i], marker='x',  color='red', markersize=10, label="Unsensed Failure")
                break


    def printHistory2Excel(self, filename: str = 'system_history.xlsx') -> None:
        """ Print the history of the system and its sensed components to an excel file """
        
        # Create a new Excel file 
        with xlsxwriter.Workbook(filename) as workbook:
            # Create a new worksheet for the system history
            worksheet = workbook.add_worksheet('System')

            # write the header for the system history sheet
            header = ['Time Step', 'System True State', 'System Sensed State']
            worksheet.write_row(0, 0, header)
            for i in range(len(self.extendedHistory)):
                worksheet.write_row(i+1, 0, [i, self.history[i], self.sensedHistory[i]])

            # add a new worksheet for each component and use its printHistory2Excel function
            for i, comp in enumerate(self.comps):
                worksheet = workbook.add_worksheet('Sensed Component ' + str(i+1))
                comp.printHistory2Excel(filename, worksheet)