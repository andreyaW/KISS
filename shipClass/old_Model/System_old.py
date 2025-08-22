from shipClass.old_Model.SensedComp_old import SensedComp
from utils.helperFunctions import SolveStructureFunction, set_x_ticks
from utils.SystemDiagram import SystemDiagram
from utils.excelFunctions import grabTruthData, addTimeSteps, addTruth, addSensed, addUnsensedFailureFormula, highlightParallels, finalFormatting
import matplotlib.pyplot as plt
import xlsxwriter


class System():
    ''' a simple model of a system composed of many sensed components'''

    def __init__(self, name, comps: list[SensedComp], parallels = None, unmanned:bool = False)-> None:
        self.name = name
        self.comps = comps
        self.parallels = parallels
        self.initializeSystem(unmanned)
        
        # # self.unmanned = unmanned

        

  # ---------------------- Simulation Functions ----------------------  
    def initializeSystem(self, unmanned): 
        """ Initialize the system and its components """
        
        for sc in self.comps: 
            if type(sc) is SensedComp:
                sc.initializeSensedComp()

        # true state of the system
        self.state = SolveStructureFunction(self.comps, self.parallels)  
        self.history = [self.state]  
        
        # sensed state of the system
        self.sensedState = SolveStructureFunction(self.comps, self.parallels)  
        self.sensedHistory = [self.sensedState]
        
        # define the states of the system based on the components
        self.states = self.comps[0].comp.states if type(self.comps[0]) is SensedComp else self.comps[0].states  # Assuming all components have the same states
        self.n = len(self.comps)                                         # number of total components in the system
        self.nPar = len(self.parallels) if self.parallels is not None else 0  # number of parallel components in the system

    def simulate(self, number_of_steps: int = 1) -> None:
        """ Simulate the system (uses simulate() from SensedComp class) """
        
        # For each step sense the state of the component
        for i in range(number_of_steps):
            
            # update the state of all the components
            for comp in self.comps:
                comp.simulate(1)
                
            # determine and store the sensed state of the system
            self.sensedState = SolveStructureFunction(self.comps, self.parallels)
            self.sensedHistory.append(self.sensedState)          # sensed state

            # determine and store the true state of the system
            self.state = SolveStructureFunction(self.comps, self.parallels, True)
            self.history.append(self.state)                      # truth state
    
    def reset(self):
        """ Reset the system to initial state (same objects as before, new histories) """
    
        # reset the state of the system
        self.state = SolveStructureFunction(self.comps, self.parallels, True)          
        self.history.append(self.state)  # append the new state to the history
        self.sensedState = SolveStructureFunction(self.comps, self.parallels) 
        self.sensedHistory.append(self.sensedState)  # append the new sensed state to the history


    def failureCheck(self):
        """ Check if the system has failed """
        if self.state == 0:  # if the system is in the failed state
            return True

        # if all components are in the working state, return false
        return False   

# ---------------------- Visualization Functions ----------------------  
    
    def check4DuplicateNames(self):
        """ Check for duplicate component names, and update the duplicates to have unique names """
        seen = set()
        for comp in self.comps:
            if comp.name in seen:
                # update this component to have a number
                i = 1
                new_name = f"{comp.name} {i+1}"
                while new_name in seen:
                    i += 1
                    new_name = f"{comp.name} {i+1}"
                comp.name = new_name
            seen.add(comp.name)
             

    def outputSystemStates(self):
        ''' output the states of the system '''
        
        # Print the header
        print("{:<15} {:<10} {:<10}".format("Component", "State", "Sensed State"))
        
        # Print the states of each component
        for i, comp in enumerate(self.comps):
            print("{:<15} {:<10} {:<10}".format(comp.name, comp.state, comp.sensedState))
        print("{:<15} {:<10} {:<10}".format(self.name, self.state, self.sensedState))
        

    def plotHistory(self, plot_comp_history: bool = False) -> None:
        
        """ Plot the ground truth and sensed history of the system of sensed components """
            
        # Create a figure and axis
        fig, ax = plt.subplots()
        
        # Plot the true and sensed history of the system
        ax.plot(self.history, marker=',', label='Truth')
        # ax.plot(self.sensedHistory, marker=',', label='Sensed')
        
        # ax.set_title('Sensed System History')
        ax.set_ylabel('State')
        ax.set_yticks(list(self.states.keys()))  
        ax.set_yticklabels(list(self.states.values()))
        
        ax.set_xlabel('Time Step')
        # ax.xticks(range(len(self.history)), [f'{i}h' for i in range(len(self.history))], rotation=45) # make x ticks for every hour
        set_x_ticks(ax, len(self.history))  # set x limits based on the history length

        ax.grid()
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  fancybox=True, shadow=True, ncol=5)
        
        # add a marker for unsensed failures
            # for i in range(len(self.history)):
            #     if self.history[i] != self.sensedHistory[i]:
            #         ax.plot(i, self.sensedHistory[i], marker='x',  color='red', markersize=10, label="Unsensed Failure")
            #         break
            
        # If bool is true, plot the history of each component on additonal subplots
        if plot_comp_history:
            for i, comp in enumerate(self.comps):
                comp.plotHistory()  # plot the history of each component    
                  
    def drawSystem(self, ax=None):
        """ Draw the system on the given axis """

        # create a new figure and axis if no axis is provided        
        if ax is None:
            fig, ax = plt.subplots()
        
        # initialize a SystemDiagram object in the given axis
        sys_diagram = SystemDiagram(ax=ax)
                
        # define (x,y) coordinates of all components using function in SystemDiagram class
        spacing = 1
        comp_size = 2
        sys_diagram.defineLocations(self, comp_size, spacing)
        
        # draw each component in the system at desired location
        for i,comp in enumerate(self.comps):     
            
            # draw current component
            x,y = sys_diagram.comp_locations[comp]
            sys_diagram.drawComp(comp, x, y, comp_size)
        
        sys_diagram.drawConnections(self,comp_size)   # draw connections between series and parallel components
            
        # sys_diagram.drawConnections()   # draw connections between series and parallel components                                
        sys_diagram.displayDiagram()      # display the diagram

# ---------------------- Data Tracking Functions ----------------------
    def printHistory2Excel(self, filename: str = 'system_history.xlsx',  worksheet=None, addComps:bool = True) -> None:
        """ Print the history of the system and its sensed components to an excel file """

        # determine important column letter numbers
        truth_col =2
        sensed_col = 3 + self.n
        f1_col = 4 + self.n*2
        
        self.check4DuplicateNames()  # check for duplicate component names and update them to be unique

        # add to the workbook using xlsxwriter
        with xlsxwriter.Workbook(filename) as workbook:

            # if no worksheet is provided, create a new workbook and worksheet
            if worksheet is None:
                worksheet = workbook.add_worksheet(self.name) 
                
            # add data to the sheet 
            num_data = len(self.history)
            for i in range(num_data):
                
                # add the time steps to the first column
                addTimeSteps(workbook, worksheet, i)

                # add truth states of the system and each sensed component to the row           
                truth_data = grabTruthData(self, i)
                
                if i == 0: 
                    sys_truth_headers = ['Sys Truth State'] + [comp.name.capitalize() + 'Truth State' for comp in self.comps]
                    addTruth(workbook, worksheet, i, truth_data, sys_truth_headers)
                else:
                    addTruth(workbook, worksheet, i, truth_data)

                # add the sensed states of te system and each sensed component to the row
                sensed_data = [self.sensedHistory[i]] + [self.comps[j].sensedHistory[i] for j in range(self.n)]
                if i == 0:
                    sys_sensed_headers = ['Sys Sensed State'] + [comp.name.capitalize() + ' Sensed State' for comp in self.comps]
                    addSensed(workbook, worksheet, i, sensed_data, sys_sensed_headers)
                else:
                    addSensed(workbook, worksheet, i, sensed_data)

                # add formula for checking if the sensed state matches the truth state
                addUnsensedFailureFormula(workbook, worksheet, i, truth_col, sensed_col, f1_col, num_data)

            # add formating for parallel components
            if self.parallels is not None:
                highlightParallels(workbook, worksheet, self.parallels, num_data, self.n)
            
            finalFormatting(worksheet, self.n)

            # add each sensed componet to its own worksheet
            if addComps:
                for i in range(self.n):
                    # create a new worksheet for each component
                    comp_name = self.comps[i].name.capitalize()
                    ws= workbook.add_worksheet(comp_name)

                    # add the history of the component to the worksheet
                    self.comps[i].printHistory2Excel(filename, worksheet=ws)

