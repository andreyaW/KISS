from shipClass.MarkovChain import MarkovChain

class Component(MarkovChain):

    def __init__(self, 
                 name: str, 
                 states: dict[int: str], 
                 transition_matrix )-> None:      
        
        """ Initialize the component as a Markov Chain object """
        self.name = name

        # inheriting from MarkovChain class (holds self.state, and self.history)
        super().__init__(states, transition_matrix)  


# ---------------------- Markov Chain Simulation ----------------------       
        
    def simulate(self, number_of_steps: int) -> None:
        """ update the state of the component """
    
        super().simulate(number_of_steps)  # Simulate the Markov Chain



    def plotHistory(self): # not sure if this is needed************************
        """ Plot the history of the Markov Chain """
        
        # Create a figure and axis
        super().plotHistory()


# ---------------------- Reliability Modelling ----------------------       
    