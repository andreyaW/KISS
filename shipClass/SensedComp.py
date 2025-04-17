from shipClass.Component import Component
from shipClass.Sensor import Sensor
from utils.helperFunctions import find_mode

import matplotlib.pyplot as plt
import numpy as np
import xlsxwriter

class SensedComp(Component, Sensor):

    """ Sensed component class that inherits from Component and Sensor classes """

    # possibly need to remake the __init__ method to initialize the sensor and components
    # can have comp_states, comp_transition_matrix, sensor_states, sensor_transition_matrix as inputs

    # def __init__(self, 
    #             comp : Component, 
    #             sensors : list[Sensor])-> None:
        
    def __init__(self, comp_states: dict[int: str] = {0: 'Failed', 1: 'Working'}, 
                 comp_transition_matrix: list[list[float]]=[[1.0, 0.0], [0.2, 0.98]],
                 sensor_states: dict[int: str] = {0: 'Failed', 1: 'Working'}, 
                 sensor_transition_matrix: list[list[float]] = [[1.0, 0.0], [0.2, 0.98]], 
                 num_sensors: int = 3, comp_name= None)-> None:

        """ Initialize the sensed component """     
        
        # initialize the component object
        if comp_name is None:
            comp_name = 'Component'
        comp = Component(comp_name, comp_states, comp_transition_matrix)
        self.comp = comp
        self.name = 'Sensed ' + comp.name               

        # initialize sensors to be attached to the component
        self.n = num_sensors
        sensors = []
        for i in range(self.n):
            sensor = Sensor('Sensor ' + str(i+1), sensor_states, sensor_transition_matrix)
            sensor.sensorReadings.append(comp.state)    # each sensors keeps track of their individual readings from the comp
            sensors.append(sensor)        
        self.sensors = sensors
        
        # sensed component attributes
        self.state = comp.state                         # ground truth state of the component       
        self.sensedState = comp.state                   # sensed states of the component
        self.sensedHistory = [self.sensedState]         # array to keep track of the sensed states of this object          
       
        # extended histories of the component and sensors (histories ignoring maintenance resets)
        self.extendedHistory = self.comp.history  
        self.extendedSensedHistory = self.sensedHistory  


# ---------------------- Monte Carlo Simulation  ----------------------       
    def senseState(self) -> None:
        """ Sense the state of the component """
              
        # iterate through each sensor and get the sensed state
        sensedStates = np.zeros(self.n)  # an array to store the sensed states
        for i in range(self.n):
            sensor = self.sensors[i]
            
            # only updates to truth if sensor works
            working_state= list(sensor.states.keys())[-1]
            if sensor.state == working_state:     
                sensedState = self.comp.state
            else:                    
                # broken sensor, assume no update is recieved and the readings remain unchanged
                last_sensed_state = sensor.sensorReadings[-1]
                sensedState = last_sensed_state

            sensor.sensorReadings.append(sensedState)       # update the sensor readings history
            sensedStates[i] = sensor.sensorReadings[-1]     # store the sensed state of the sensor to array for solving
            
        # the overall sensed state is the most common state sensed between the sensors
        self.sensedState  = int(find_mode(sensedStates))
        self.sensedHistory.append(self.sensedState)         # update the sensed components sensed history
        self.state = self.comp.state                        # update the ground truth to match the component state


    def simulate(self, number_of_steps: int = 1) -> None:
        """ Simulate the sensed component (uses simulate() from Component and Sensor classes) """
        # For each step, simulate comp and sensors then sense the new state
        for i in range(number_of_steps):
            self.comp.simulate()   # update the comp state
            for sensor in self.sensors:
                sensor.simulate()  # update the sensor state
            self.senseState()       # determines and stores the state of the sensed component


    def reset(self):
        """ Reset the sensed component to initial state (same objects as before, new histories) """
        self.extendedHistory = self.extendedHistory + self.comp.extendedHistory
        self.extendedSensedHistory = self.extendedSensedHistory + self.sensedHistory
        self.comp.reset()
        for sensor in self.sensors:
                sensor.reset()
                sensor.sensorReadings = [self.comp.state]  # reset the sensor readings history and store initial state
        self.sensedHistory = [self.comp.state]             # reset the sensed history of the sensed component and store initial state
        self.state = self.comp.state                       # reset the ground truth state of the component


# ---------------------- Plotting + Output ----------------------

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


        
    def printHistory2Excel(self, filename: str = 'sensedComp_history.xlsx', worksheet=None) -> None:
        """ 
        This function is used to print the history of the sensed component to an excel file. 
        Each sensed component has one page with its true states, sensor states and sensed states.         
        """

        if worksheet is not None:
            # if a worksheet is provided, write to that worksheet
            worksheet.write_row(0, 0, ['Time Step', 'Truth State'] + ['Sensor ' + str(i+1) for i in range(self.n)] + ['Sensed State'])
            for i in range(len(self.extendedHistory)):
                sensor_data = [self.sensors[j].extendedHistory[i] for j in range(self.n)]
                row = [i, self.comp.extendedHistory[i]] + sensor_data + [self.extendedSensedHistory[i]]
                worksheet.write_row(i+1, 0, row)
        
        # if no worksheet is provided, create a new workbook and worksheet
        else:    
            with xlsxwriter.Workbook(filename) as workbook:
                worksheet = workbook.add_worksheet(self.name) 

                # write the headers in the first row
                sensor_headers = ['Sensor ' + str(i+1) for i in range(self.n)]
                headers = ['Time Step', 'Truth State'] + sensor_headers + ['Sensed State']
                worksheet.write_row(0, 0, headers)

                # write the data into the following rows
                for i in range(len(self.comp.extendedHistory)): 
                    sensor_data = [self.sensors[j].extendedHistory[i] for j in range(self.n)]           # get the sensor data for this time step
                    row = [i, self.comp.extendedHistory[i]] + sensor_data + [self.extendedSensedHistory[i]]
                    worksheet.write_row(i+1, 0, row)
        