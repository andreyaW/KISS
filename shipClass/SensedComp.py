from shipClass.Component import Component
from shipClass.Sensor import Sensor
from utils.helperFunctions import get_key_by_value

import matplotlib.pyplot as plt
import statistics as stats

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

# ---------------------- Useful Methods  ----------------------       

    def senseState(self) -> None:
        """ Sense the state of the component """
        # handles the case of multiple sensors differently than single sensor
        n = len(self.sensors) if isinstance(self.sensors, list) else 1    # number of sensors
        if n > 1:
            # list to store the multiple sensedStates from each sensor
            sensedStates = []    
            sensorStates = []
            # iterate through each sensor and get the sensed state
            for i in range(n):
                sensor = self.sensors[i]
                sensorStates.append(sensor.state)  # get the state of the sensor as a number

                # get the state of the sensor as a number
                sensor_state = get_key_by_value(sensor.states, sensor.state)
                working_state= list(sensor.states.keys())[-1]

                # if the sensor is working, update sensed state to match the current comp_state
                if sensor_state == working_state: 
                    sensedStates.append(self.comp.state)
                else:
                    # if the sensor is broken, assume no update has been recieved since previous sensed state
                    sensedStates.append(self.sensedState)

            # get the most common sensed state from the sensors and update the sensed state
            print('the sensor states are : ' , sensorStates)
            print('the sensed states from the component are', sensedStates)

            self.sensedState = stats.mode(sensedStates)

        else:            
            sensor = self.sensors

            # get the state of the sensor as a number
            sensor_state = get_key_by_value(sensor.states, sensor.state)
            working_state= list(sensor.states.keys())[-1]
            
            # if the sensor is working, update sensed state to match the current comp_state
            if sensor_state == working_state: 
                self.sensedState = self.comp.state  # only updates to truth if sensor works

        # Update the true state of the component always
        self.state = comp_state = self.comp.state  # update truth


# ---------------------- Monte Carlo Simulation  ----------------------       
    def simulate(self, number_of_steps: int) -> None:
        """ Simulate the sensed component (uses simulate() from Component and Sensor classes) """
        
        # For each step sense the state of the component
        for i in range(number_of_steps):
            
            # update the state of the component and sensors
            self.comp.simulate(1)
            n = len(self.sensors) if isinstance(self.sensors, list) else 1    # number of sensors
            if n > 1:
                for sensor in self.sensors:
                    sensor.simulate(1)    # functions for multiple sensors not implemented yet
            else:    
                self.sensors.simulate(1)

            # determine and store the state of the sensed component
            state = self.senseState()
            self.history.append(self.state)                 # truth
            self.sensedHistory.append(self.sensedState)     # sensed state



    def plotHistory(self, plot_sensor_history: bool = False) -> None:
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



        # create a second y-axis for the sensor history
        if plot_sensor_history:
            ax2 = ax.twinx()
            n = len(self.sensors) if isinstance(self.sensors, list) else 1    # number of sensors
            if n > 1:
                for sensor in self.sensors:
                    sensor_history = sensor.history
                    ax2.plot(sensor_history, marker=',', label='Sensor History', color='orange')
            else:
                sensor_history = self.sensors.history
                ax2.plot(sensor_history, marker=',', label='Sensor History', color='orange')    
            ax2.set_ylabel('Sensor State')
            ax2.legend(loc='upper right')

        
        # Show the plot
        plt.show()
