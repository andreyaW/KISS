from shipClass.MarkovChain import MarkovChain

class Component(MarkovChain):

    def __init__(self, 
                 name: str, 
                 states: dict[int: str], 
                 transition_matrix )-> None:      
        
        """ Initialize the component as a Markov Chain object """
        self.name = name

        # inheriting from MarkovChain class 
        # (super() holds self.state, self.history, and simulate(), plotHistory() and other methods)
        super().__init__(states, transition_matrix)  

# ---------------------- Reliability Modelling ----------------------       
    