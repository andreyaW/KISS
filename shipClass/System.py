from shipClass.SensedComp import SensedComp

import numpy as np

class System():
    ''' a simple model of a system composed of many sensed components'''

    def __init__(self, name, comps: list[SensedComp], parallels = None)-> None:
        self.name = name
        self.comps = comps
        self.parallels = parallels
        self.history = []
        self.state = self.SolveStructureFunction()
        
    def simulate(self, number_of_steps: int) -> None:
        ''' update the state of the system '''
        current_time = 0
        while current_time < number_of_steps:
            for comp in self.components:
                comp.simulate(1)            
            self.state = self.SolveStructureFunction()
            self.history.append(self.state)
            current_time += 1
            
    

    def SolveStructureFunction(self):

        ''' calculate the structure function of the system '''
        
        Xi = self.getStates()
        phi = min(Xi)       # for series comps
        # phi = max(Xi)      # for parallel comps

        return phi



        # for i,state in enumerate(comp_states):
        #     if state == 0 or comp.sensedState == 1:
        #         Xi[i] = 1
        #     if comp.sensedState >= 2:
        #         Xi[i] = 0  
        
        
        
