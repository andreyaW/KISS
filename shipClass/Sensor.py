
from shipClass.MarkovChain import MarkovChain

class Sensor(MarkovChain):

    def __init__(self, 
                 name: str, 
                 states: dict[int: str], 
                 transition_matrix )-> None:      
        
        """ Initialize the component  """
        self.name = name

        # inheriting from MarkovChain class 
        # (super() holds self.state, self.history, and simulate(), plotHistory() and other methods)
        super().__init__(states, transition_matrix)
        self.sensorReadings = [] # list of sensor readings from the component it is sensing