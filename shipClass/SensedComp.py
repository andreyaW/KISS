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

    def __init__(self, 
                comp : Component, 
                sensors : list[Sensor])-> None:
        
        """ Initialize the sensed component """
        self.name = 'Sensed ' + comp.name    # name of the sensed component
        self.comp = comp
        self.sensors = sensors
        
        # determine the number of sensors
        self.n = len(self.sensors) if isinstance(self.sensors, list) else 1  
         
        if self.n > 1:
            for sensor in sensors:
                sensor.sensorReadings.append(comp.state)  # allow sensors to keep a log of the readings they have taken 
        else:
            self.sensors.sensorReadings. append(comp.state)        
        
        # true states of the component
        self.state = comp.state             
        self.history = []                   

        # sensed states of the component
        self.sensedState = comp.state             
        self.sensedHistory = []            

       

# ---------------------- Useful Methods  ----------------------       

    def senseState(self) -> None:
        """ Sense the state of the component """
    
        # multiple sensors logic
        if self.n > 1:
            sensedStates = np.zeros(self.n)  # create an array of zeros to store the sensed states
               
            # iterate through each sensor and get the sensed state
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
            
        # single sensor logic
        else:            
            sensor = self.sensors

            # only updates to truth if sensor works
            working_state= list(sensor.states.keys())[-1]
            if sensor.state == working_state: 
                sensor.sensorReadings.append(self.comp.state)  # updates sensors to keep a log of readings they have taken
            else:
                # broken sensor, assume no update is recieved and the reading remain unchanged
                last_sensed_state = sensor.sensorReadings[-1]
                sensor.sensorReadings.append(last_sensed_state)
                
            self.sensedState = sensor.sensorReadings[-1]
                
        # update true state of the component always
        self.state = self.comp.state  

# ---------------------- Monte Carlo Simulation  ----------------------       
    def simulate(self, number_of_steps: int) -> None:
        """ Simulate the sensed component (uses simulate() from Component and Sensor classes) """
        
        # For each step sense the state of the component
        for i in range(number_of_steps):
            
            # update the state of the component
            self.comp.simulate(1)
            
            # update the state of all the sensors
            if self.n > 1:
                for sensor in self.sensors:
                    sensor.simulate(1)
            else:    
                self.sensors.simulate(1)
            
            # determine and store the state of the sensed component
            self.senseState()
            self.history.append(self.state)                 # truth
            self.sensedHistory.append(self.sensedState)     # sensed state



    def plotHistory(self, plot_sensor_history: bool = False) -> None:
        """ Plot the ground truth and sensed history of the Markov Chain """

        # Create a figure and axis
        fig, ax = plt.subplots()
 
        # Plot the true and sensed history          
        ax.plot(self.history, marker=',', label='Truth')
        ax.plot(self.sensedHistory, marker=',', label='Sensed')

        # add a marker for unsensed failures
        for i in range(len(self.history)):
            if self.history[i] != self.sensedHistory[i]:
                # y_location = get_key_by_value(self.comp.states, self.sensedHistory[i])
                ax.plot(i, self.sensedHistory[i], marker='x',  color='red', markersize=10, label="Unsensed Failure")
                break   # only show the first unsensed failure
            
        # Set the title and labels
        ax.set_title('Sensed Component History')
        ax.set_xlabel('Time Step')
        ax.set_ylabel('State')
        ax.set_yticks(list(self.comp.states.keys()))
        ax.set_yticklabels(list(self.comp.states.values()))
        ax.set_xlim(0, len(self.history))
        ax.legend()
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
            ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
            fancybox=True, shadow=True, ncol=5)

        # Show the plot
        plt.grid()
        plt.show()