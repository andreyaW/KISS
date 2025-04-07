from shipClass.SensedComp import SensedComp

import numpy as np

class System():
    ''' a simple model of a system composed of many sensed components'''

    def __init__(self, comps: list[SensedComp], parallels = None)-> None:
                
        self.components = comps
        self.parallels = parallels
        self.history = []
        self.state = determineSysState()
        
        
    def simulate(self, number_of_steps: int) -> None:
        ''' update the state of the system '''
        
        for comp in self.components:
            comp.simulate(number_of_steps)            
        self.state = determineSysState()
        
        
    def determineSysState(self):
        
        ''' determine the state of the system based on the states of its components '''
        states = np.zeros(len(self.components))
        for i,comp in enumerate(self.components):
            
            states[i] = comp.sensedState
            

        # if self.parallels is not None:            
        # self.history.append(self.state)

            return states
        

    def structureFunction():

        ''' calculate the structure function of the system '''
        
        Xi = np.zeros(len(self.components))
        for i,comp in enumerate(self.components):
            
            if comp.sensedState == 0 or comp.sensedState == 1:
                Xi[i] = 1
                
            if comp.sensedState >= 2:
                Xi[i] = 0  
        
        return 1 - np.prod(1 - Xi)
        
        
        # # for series comps 
        # phi = np.prod(xi)
        
        # # for parallel comps
        # phi = 1 - np.prod(1 - xi)
        
        
        
        
