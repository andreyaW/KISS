from shipClass.SensedComp import SensedComp

import matplotlib.pyplot as plt

class System():
    ''' a simple model of a system composed of many sensed components'''

    def __init__(self, name, comps: list[SensedComp], parallels = None)-> None:
        self.name = name
        self.comps = comps
        self.parallels = parallels
        self.states = self.comps[0].comp.states
                
        # true state of the system
        self.state = self.SolveStructureFunction()  
        self.history = [self.state]  
        
        # sensed state of the system
        self.sensedState = self.SolveStructureFunction()  
        self.sensedHistory = [self.sensedState]  
        
    # ---------------------- Determination of System State ----------------------       

    def getStates(self, list_of_comps, bool = False) -> list:     
        """gets the states of the systems components """
        
        states = []            # create list to store the states       
        
        # if bool is True, get the TRUE states of the components
        if bool: 
            for i,comp_idx in enumerate(list_of_comps):
                states.append(self.comps[comp_idx].state)   
            return states
        
        # if bool is False, get the SENSED states of the components 
        else: 
            for i,comp_idx in enumerate(list_of_comps):
                states.append(self.comps[comp_idx].sensedState)   
            return states

        
    def SolveStructureFunction(self, bool = False) -> int:
        ''' calculate the structure function of the system '''
        Xi = []  # list to store the states of the system
                
        if self.parallels is not None:
            n = len(self.parallels)  # number of parallel sets
            if n >1: 
                pass # functionality not yet implemented for multiple parallel sets
            else:
                # get the states of the components in parallel
                states = self.getStates(self.parallels,bool)
                
                # determine the state of the set using structure function then, 
                # add the state of the parallel sets to overall system list
                Xi= Xi + max(states)      
                        
        # considering all other components in series
        series_comps = []  # list to store the states of series components            

        # if there are components in parallel, get the idx of the series components
        if self.parallels is not None: 
            for i in range(len(self.comps)):
                if i not in self.parallels:
                    series_comps.append(i)  
        # else get the idx of all components
        else:
            series_comps = list(range(len(self.comps)))  # get the index of all components
        
        Xi = Xi + self.getStates(series_comps, bool)
        phi = min(Xi)               # considering series comps
        
        return phi
    
    

    def outputSystemStates(self):
        ''' output the states of the system '''
        
        # Print the header
        print("{:<10} {:<5} {:<10}".format("Component", "State", "Sensed State"))
        
        # Print the states of each component
        for i, comp in enumerate(self.comps):
            print("{:<10} {:<5} {:<10}".format(comp.name, comp.state, comp.sensedState))
        print("System State:", self.state)  
        
        
        
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
        
        # # add a marker for unsensed failures
        # for i in range(len(self.history)):
        #     if self.history[i] != self.sensedHistory[i]:
        #         # y_location = get_key_by_value(self.comps[0].states, self.sensedHistory[i])
        #         ax.plot(i, self.sensedHistory[i], marker='x',  color='red', markersize=10, label="Unsensed Failure")
        #         break
        
# ---------------------- Markov Chain Simulation ----------------------  
#      
    def simulate(self, number_of_steps: int) -> None:
        """ Simulate the system (uses simulate() from SensedComp class) """
        
        # For each step sense the state of the component
        for i in range(number_of_steps):
            
            # update the state of all the components
            for comp in self.comps:
                comp.simulate(1)
                
            # determine and store the sensed state of the system
            self.sensedState = self.SolveStructureFunction()
            self.sensedHistory.append(self.sensedState)          
            
            if self.sensedHistory[-1] > self.sensedHistory[-2]:  # if the sensed state has improved
                print( 'There has been an error in simulation') # error messsage 
                break
            
            
            # determine and store the true state of the system
            self.state = self.SolveStructureFunction(True)
            self.history.append(self.state)                     # truth
