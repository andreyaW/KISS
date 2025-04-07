from shipClass.SensedComp import SensedComp

import numpy as np

class System():
    ''' a simple model of a system composed of many sensed components'''

    def __init__(self, comps: list[SensedComp], parallels = None)-> None:
                
        self.components = comps
        self.parallels = parallels
        self.history = []
        self.state = SolveStructureFunction()
        
    def simulate(self, number_of_steps: int) -> None:
        ''' update the state of the system '''
        
        while current_time < number_of_steps:
            for comp in self.components:
                comp.simulate(1)            
                self.state = SolveStructureFunction()
                self.history.append(self.state)


    def SolveStructureFunction(self):

        ''' calculate the structure function of the system '''
        
        Xi = np.zeros(len(self.components))
        for i,comp in enumerate(self.components):
            
            if comp.sensedState == 0 or comp.sensedState == 1:
                Xi[i] = 1
                
            if comp.sensedState >= 2:
                Xi[i] = 0  

        # for series comps 
        phi = min(Xi)

        # # for parallel comps
        # phi = max(Xi)

        return phi
        
        
        
