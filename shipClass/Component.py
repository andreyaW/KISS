from shipClass.MarkovChain import MarkovChain

class Component(MarkovChain):

    def __init__(self, 
                 name: str, 
                 states: dict[int: str], 
                 transition_matrix )-> None:      
        
        """ Initialize the component as a Markov Chain object """
        
        # inheriting from MarkovChain class 
        # (super() holds self.state, self.history, and simulate(), plotHistory() and other methods)
        super().__init__(states, transition_matrix)  

        # declare component attributes
        self.name = name
        self.extendedHistory = []  # array to keep track of the extended history of the component ( history ignoring resets )

# ---------------------- Reliability Modelling ----------------------       
    def reset(self):
        self.extendedHistory = self.extendedHistory + self.history[1:]  # Append the history to the extended history
        super().reset()  # Call the reset method of the parent class
