from shipClass.Component import Component
from shipClass.Sensor import Sensor

import matplotlib.pyplot as plt

class SensedComp(Component, Sensor):

    def __init__(self, 
                comp : Component, 
                sensors : list[Sensor])-> None:
        
        """ Initialize the sensed component """
        self.comp = comp
        self.sensors = sensors
        
        self.state = comp.state             # truth
        self.history = []                   # truth history

        self.sensedState = comp.state       # sensed state
        self.sensedHistory = []             # sensed history

    def senseState(self) -> None:
        """ Sense the state of the component """
        
        # store the state of the sensors
        n = len(self.sensors) if isinstance(self.sensors, list) else 1    # number of sensors
        if n > 1:
            pass
        else:
            sensor = self.sensors
            
            # what is sensor state 
            sensor_state = sensor.currentState()
            if sensor_state == 'Working': 
                self.sensedState = self.comp.state  # only updates to truth if sensor works

        # Update the true state of the component
        self.state = comp_state = self.comp.currentState()  # update truth



    def simulate(self, number_of_steps: int) -> None:
        """ Simulate the sensed component """
        
        # For each step sense the state of the component
        for i in range(number_of_steps):
            
            # get state before update
            self.senseState()
            
            # update the state of the component and sensors
            self.comp.simulate(1)
            self.sensors.simulate(1)

            # store the state of the sensed component
            self.history.append(self.state)                 # truth
            self.sensedHistory.append(self.sensedState)     # sensed state
            

    def plotHistory(self):
        """ Plot the ground truth and sensed history of the Markov Chain """

        # Create a figure and axis
        fig, ax = plt.subplots()
        
        # Plot the true and sensed history
        ax.plot(self.history, marker=',', label='Truth')
        ax.plot(self.sensedHistory, marker=',', label='Sensed')
        
        # Set the title and labels
        ax.set_title('Sensed Component History')
        ax.set_xlabel('Time Step')
        ax.set_ylabel('State')
        ax.legend()
        
        # Show the plot
        plt.show()
