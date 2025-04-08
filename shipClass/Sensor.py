
from shipClass.MarkovChain import MarkovChain

class Sensor(MarkovChain):

    def __init__(self, 
                 name: str, 
                 states: dict[int: str], 
                 transition_matrix )-> None:      
        
        """ Initialize the component  """
        self.name = name

        # inheriting from MarkovChain class
        super().__init__(states, transition_matrix)
        
# ---------------------- Simulation ----------------------       
        
    def simulate(self, number_of_steps: int) -> None:
        """ update the state of the component """
        
        # Simulate the Markov Chain
        super().simulate(number_of_steps)

    def plotHistory(self):
        """ Plot the history of the Markov Chain """
        
        # Create a figure and axis
        super().plotHistory()


    