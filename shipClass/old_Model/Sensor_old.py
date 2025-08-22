
from shipClass.MarkovChain import MarkovChain

class Sensor(MarkovChain):

    def __init__(self, 
                 name: str, accr: float = 0.98 )-> None:      
        
        """ Initialize the component  """
        # inheriting from MarkovChain class 
        # (super() holds self.state, self.history, and simulate(), plotHistory() and other methods)

        states: dict[int: str] = {0 : 'malfunctioning', 
                                  1 : 'working'}
        transition_matrix = [[1, 0], [1-accr, accr]]
        super().__init__(states, transition_matrix)

        # declare sensor attributes        
        self.name = name
        self.readings = [] # list of sensor readings from the component it is sensing

# ---------------------- Useful Methods  ----------------------