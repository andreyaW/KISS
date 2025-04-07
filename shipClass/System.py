from shipClass.SensedComp import SensedComp

import numpy as np

class System():
    ''' a simple model of a system composed of many sensed components'''

    def __init__(self, name, comps: list[SensedComp], parallels = None)-> None:
        self.name = name
        self.comps = comps
        self.parallels = parallels
        self.history = []
        self.SolveStructureFunction()            # sets initial state and updates it to the history
        
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
        
        Xi = np.zeros(len(self.comps))
        
        # grab the state of each comp (should be a number value)
        for i,comp in enumerate(self.comps):
            
                        
            Xi[i] = comp.sensedState
            
            # if comp.sensedState == 0 or comp.sensedState == 1:
            #     Xi[i] = 1
            # if comp.sensedState >= 2:
            #     Xi[i] = 0  

        # structure function for series comps 
        phi = min(Xi)

        # structure function for parallel comps
        # phi = max(Xi)

        self.state = phi
        self.history.append(phi)
        
        
        
        
        
