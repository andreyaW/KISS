from shipClass.Component import Component
from utils.helperFunctions import SolveStructureFunction, set_x_ticks
from utils.excelFunctions import grabTruthData, addTimeSteps, addTruth, addSensed, addUnsensedFailureFormula, highlightParallels, finalFormatting
from utils.SystemDiagram import SystemDiagram


import xlsxwriter
import matplotlib.pyplot as plt

class System():

    def __init__(self, name, comps: list[Component], parallels = None, repairable:bool = False)-> None:

        """ a simple model of a system composed of many sensed components

            Parameters
            ----------
            name: str
                The name of the system.
            comps: list[Component]
                A list of components that make up the system.
            parallels: list[tuple[int]]
                A list of parallel component sets, where each set is represented as a tuple of component indices.
            repairable: bool
                A flag indicating whether the system is repairable (default is False).
        """

        self.name = name
        self.comps = comps
        self.parallels = parallels
        self.initialize(repairable)


#------------------- Simulation Functions ----------------
    def initialize(self, repairable:bool = False):
        for comp in self.comps:
            comp.initialize(repairable)
        
        # true state of the system
        self.state = SolveStructureFunction(self.comps, self.parallels)  
        self.history = [self.state]  
        
        # define the states of the system based on the components
        self.states = self.comps[0].states  # Assuming all components have the same states
        self.n = len(self.comps)                                         # number of total components in the system

    def simulate(self, num_steps): 
        for _ in range(num_steps):
            for comp in self.comps:
                comp.simulate(1)
            self.state = SolveStructureFunction(self.comps, self.parallels)  
            self.history.append(self.state)

# -------------- Functions for Plotting --------------------------
    def plotHistory(self, plot_comp_history: bool = False) -> None:
        
        """ Plot the ground truth and sensed history of the system of sensed components """
            
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


# --------------- Functions for Printing to Excel ----------------
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
