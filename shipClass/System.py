from shipClass.SensedComp import SensedComp

import numpy as np

class System():
    ''' a simple model of a system composed of many sensed components'''

    def __init__(self, comps: list[SensedComp], parallels = None)-> None:
                
        self.components = comps
        self.parallels = parallels
        self.history = []
        self.state = self.SolveStructureFunction()
        
    def simulate(self, number_of_steps: int) -> None:
        ''' update the state of the system '''
        
        while current_time < number_of_steps:
            for comp in self.components:
                comp.simulate(1)            
                self.state = SolveStructureFunction()
                self.history.append(self.state)


    def get_key_by_value(my_dict, value):
        """
        Returns the key associated with the given value in the dictionary.
        If the value is not found, it returns None. If multiple keys have the same value,
        it returns the first key found.
        """
        for key, val in my_dict.items():
            if val == value:
                return key
        return None



    def getStates(self):
        """gets the states of the systems components as number values instead of strings"""
        
        comp_states = np.zeros(len(self.components))
        for comp in self.components:
            comp_states[i] = get_key_by_value(comp.states, comp.sensedState)

        return comp_states



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
        
        
        
