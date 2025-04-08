from shipClass.Component import Component
from shipClass.Sensor import Sensor

from utils.helperFunctions import get_key_by_value

import matplotlib.pyplot as plt

class SensedComp(Component, Sensor):

    """ Sensed component class that inherits from Component and Sensor classes """

    # possibly need to remake the __init__ method to initialize the sensor and components
    # can have comp_states, comp_transition_matrix, sensor_states, sensor_transition_matrix as inputs

    def __init__(self, 
                comp : Component, 
                sensors : list[Sensor])-> None:
        
        """ Initialize the sensed component """
        self.comp = comp
        self.sensors = sensors
        self.name = 'Sensed ' + comp.name    # name of the sensed component
        
        # true states of the component
        self.state = comp.state             
        self.history = []                   

        # sensed states of the component
        self.sensedState = comp.state             
        self.sensedHistory = []            

    def senseState(self) -> None:
        """ Sense the state of the component """
        
        # store the state of the sensors
        n = len(self.sensors) if isinstance(self.sensors, list) else 1    # number of sensors
        if n > 1:
            pass    # functions for multiple sensors not implemented yet
        else:            
            # current sensor state 
            sensor_state = get_key_by_value(self.sensor.states, self.sensor.state)  # get the state of the sensor as a number
            working_state_val = list(sensor.states.keys())[-1]
            
            # if the sensor is working, update state to match the comp_state
            if sensor_state == working_state_val: 
                self.sensedState = self.comp.state  # only updates to truth if sensor works

        # Update the true state of the component always
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

        # # add a marker for unsensed failures
        # for i in range(len(self.history)):
        #     if self.history[i] != self.sensedHistory[i]:
        #         ax.plot(self.history[i],  marker='x', color='red', markersize=10)
        
        # Set the title and labels
        ax.set_title('Sensed Component History')
        ax.set_xlabel('Time Step')
        ax.set_ylabel('State')
        ax.legend()
        
        # Show the plot
        plt.show()
