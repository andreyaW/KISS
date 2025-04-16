
from shipClass.MarkovChain import MarkovChain

class Sensor(MarkovChain):

    def __init__(self, 
                 name: str, 
                 states: dict[int: str], 
                 transition_matrix )-> None:      
        
        """ Initialize the component  """
        # inheriting from MarkovChain class 
        # (super() holds self.state, self.history, and simulate(), plotHistory() and other methods)
        super().__init__(states, transition_matrix)

        # declare sensor attributes        
        self.name = name
        self.sensorReadings = [] # list of sensor readings from the component it is sensing
        self.extendedHistory = self.history
        self.extendedReadings = self.sensorReadings        


# ---------------------- Useful Methods  ----------------------
    def reset(self):
        self.extendedHistory = self.extendedHistory + self.history[1:]  # Append the history to the extended history
        self.extendedReadings = self.extendedReadings + self.sensorReadings[1:]  # Append the sensor readings to the extended readings
        super().reset()  # Call the reset method of the parent class
