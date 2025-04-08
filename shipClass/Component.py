from shipClass.MarkovChain import MarkovChain

class Component(MarkovChain):

    def __init__(self, 
                 name: str, 
                 states: dict[int: str], 
                 transition_matrix )-> None:      
        
        """ Initialize the component  """
        self.name = name
        self.state = states[0]  # initial state

        # inheriting from MarkovChain class
        super().__init__(states, transition_matrix) 

# ---------------------- Markov Chain Simulation ----------------------       
        
    def simulate(self, number_of_steps: int) -> None:
        """ update the state of the component """
        
        # Simulate the Markov Chain
        super().simulate(number_of_steps)
        self.state = super().currentState()
        
        

    def plotHistory(self):
        """ Plot the history of the Markov Chain """
        
        # Create a figure and axis
        super().plotHistory()
        
        
        


# ---------------------- Reliability Modelling ----------------------       
    def reliability(self, time: int) -> float:
        """ Calculate the reliability of the component """
        
        # Calculate the reliability of the Markov Chain
        return super().reliability(time)
    