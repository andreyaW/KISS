from shipClass.Component import Component
from shipClass.Sensor import Sensor
from utils.helperFunctions import get_key_by_value
from utils.helperFunctions import find_mode

import matplotlib.pyplot as plt
import numpy as np

class SensedComp(Component, Sensor):

    """ Sensed component class that inherits from Component and Sensor classes """

    # possibly need to remake the __init__ method to initialize the sensor and components
    # can have comp_states, comp_transition_matrix, sensor_states, sensor_transition_matrix as inputs

    # def __init__(self, 
    #             comp : Component, 
    #             sensors : list[Sensor])-> None:
        
    def __init__(self, comp_states: dict[int: str], 
                 comp_transition_matrix: list[list[float]],
                 sensor_states: dict[int: str], 
                 sensor_transition_matrix: list[list[float]], 
                 num_sensors: int, comp_name= None)-> None:

        """ Initialize the sensed component """     
        
        # initialize the component object
        if comp_name is None:
            comp_name = 'Component'
        comp = Component(comp_name, comp_states, comp_transition_matrix)
        self.comp = comp
        self.name = 'Sensed ' + comp.name               
        self.state = comp.state                         # ground truth state of the component       

        # initialize sensors to be attached to the component
        self.n = num_sensors
        sensors = []
        for i in range(self.n):
            sensor = Sensor('Sensor ' + str(i+1), sensor_states, sensor_transition_matrix)
            sensor.sensorReadings.append(comp.state)    # array for each sensors to keep track of their individual readings 
            sensors.append(sensor)        
        self.sensors = sensors
        self.sensedState = comp.state                   # sensed states of the component
        self.sensedHistory = [self.sensedState]                         # array to keep track of the sensed states of this object          
       

# ---------------------- Useful Methods  ----------------------       

    def senseState(self) -> None:
        """ Sense the state of the component """
              
        # iterate through each sensor and get the sensed state
        sensedStates = np.zeros(self.n)  # an array to store the sensed states
        for i in range(self.n):
            sensor = self.sensors[i]
            
            # only updates to truth if sensor works
            working_state= list(sensor.states.keys())[-1]
            if sensor.state == working_state:     
                sensor.sensorReadings.append(self.comp.state)  # updates sensors to keep a log of readings they have taken
            else:                    
                # broken sensor, assume no update is recieved and the readings remain unchanged
                last_sensed_state = sensor.sensorReadings[-1]
                sensor.sensorReadings.append(last_sensed_state)
            
            sensedStates[i] = sensor.sensorReadings[-1]    
            
        # update the overall sensed state to the most common sensed state from all sensors
        self.sensedState  = find_mode(sensedStates)
        self.sensedHistory.append(self.sensedState)         # update the sensed state history

        # update true state of the component always
        self.state = self.comp.state                        # ground truth history automatically updated in the component class

# ---------------------- Monte Carlo Simulation  ----------------------       
    def simulate(self, number_of_steps: int) -> None:
        """ Simulate the sensed component (uses simulate() from Component and Sensor classes) """
        
        # For each step, simulate comp and sensors then sense the new state
        for i in range(number_of_steps):
            
            # update the state of the component
            self.comp.simulate(1)
            
            # update the state of all the sensors
            for sensor in self.sensors:
                sensor.simulate(1)

            # determine and store the state of the sensed component
            self.senseState()


    def reset(self):
        """ Reset the sensed component to initial state (same objects as before, new histories)"""
        self.comp.reset()
        for sensor in self.sensors:
                sensor.reset()
                sensor.sensorReadings = []  # reset the sensor readings history
                

        
    def plotHistory(self, plot_sensor_history: bool = False) -> None:
        """ Plot the ground truth and sensed history of the Markov Chain """

        # Create a figure and axis
        fig, ax = plt.subplots()
 
        # Plot the true and sensed history          
        ax.plot(self.comp.history, marker=',', label='Truth')
        ax.plot(self.sensedHistory, marker=',', label='Sensed')

        # add a marker for unsensed failures
        for i in range(len(self.comp.history)):
            if self.comp.history[i] != self.sensedHistory[i]:
                # y_location = get_key_by_value(self.comp.states, self.sensedHistory[i])
                ax.plot(i, self.sensedHistory[i], marker='x',  color='red', markersize=10, label="Unsensed Failure")
                break   # only show the first unsensed failure
            
        # Set the title and labels
        ax.set_title('Sensed Component History')
        ax.set_xlabel('Time Step')
        ax.set_ylabel('State')
        ax.set_yticks(list(self.comp.states.keys()))
        ax.set_yticklabels(list(self.comp.states.values()))
        ax.set_xlim(0, len(self.comp.history))
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                  fancybox=True, shadow=True, ncol=5)
        plt.grid()

        # (Optional) create a second plot for the sensor history
        if plot_sensor_history:
            # ax2 = ax.twinx()
            fig, ax2 = plt.subplots()
            if self.n > 1:
                for i,sensor in enumerate(self.sensors):
                    ax2.plot(sensor.history,',--', label= 'Sensor '+  str(i+1) + ' History')
            else:
                sensor_history = self.sensors.history
                ax2.plot(sensor_history, marker=',', label='Sensor History')    
            ax2.set_ylabel('Sensor State')
            ax2.set_yticks(list(self.sensors[0].states.keys()))
            ax2.set_yticklabels(list(self.sensors[0].states.values()))
            ax2.set_xlim(0, len(self.comp.history))
            ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
            fancybox=True, shadow=True, ncol=5)
            

        # Show the plot
        plt.grid()
        plt.show()