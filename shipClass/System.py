from shipClass.SensedComp import SensedComp
from utils.helperFunctions import get_key_by_value

import numpy as np

class System():
    ''' a simple model of a system composed of many sensed components'''

    def __init__(self, name, comps: list[SensedComp], parallels = None)-> None:
        self.name = name
        self.comps = comps
        self.parallels = parallels
        self.history = []
        self.state = self.SolveStructureFunction()
        self.states = self.comps[0].comp.states

    # ---------------------- Determination of System State ----------------------       

    def getStates(self):
        """gets the states of the systems components as number values instead of strings"""
        
        comp_states = np.zeros(len(self.comps))
        for i,sensed_comp in enumerate(self.comps):
            comp_states[i] = get_key_by_value(sensed_comp.comp.states, sensed_comp.sensedState)
        return comp_states

    def SolveStructureFunction(self):
        ''' calculate the structure function of the system '''
        
        Xi = self.getStates()
        phi = min(Xi)       # for series comps
        # phi = max(Xi)       # for parallel comps
        return phi

    def outputSystemStates(self):
        ''' output the states of the system '''
        
        # Print the header
        print("{:<10} {:<5} {:<10}".format("Component", "State", "Sensed State"))
        
        # Print the states of each component
        for i, comp in enumerate(self.comps):
            print("{:<10} {:<5} {:<10}".format(comp.name, comp.state, comp.sensedState))
        print("System State:", self.states[self.state])  # get the state of the system as a number
# ---------------------- Markov Chain Simulation ----------------------  
#      
    # def simulate(self, number_of_steps: int) -> None:
    #     ''' update the state of the system '''
    #     current_time = 0
    #     while current_time < number_of_steps:
    #         for comp in self.components:
    #             comp.simulate(1)            
    #         self.state = self.SolveStructureFunction()
    #         self.history.append(self.state)
    #         current_time += 1