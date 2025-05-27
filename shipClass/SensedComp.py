from shipClass.Component import Component
from shipClass.Sensor import Sensor
from utils.helperFunctions import find_mode
from utils.excelFunctions import addTimeSteps, addTruth, addSensed, addUnsensedFailureFormula, addSensorFailureFormula, finalFormatting

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
        
    def __init__(self, comp_name= None, 
                 comp_states: dict[int: str] = {0: 'Failed', 
                                                      1: 'Working'}, 
                 comp_transition_matrix: list[list[float]]=[[1.0, 0.0], 
                                                            [0.02, 0.98]],  
                 sensor_states: dict[int: str] = {0: 'Failed', 
                                                  1: 'Working'}, 
                 sensor_transition_matrix: list[list[float]] = [[1, 0],
                                                                [0.15, 0.85]], 
                 num_sensors: int = 3)-> None:

        """ Initialize the sensed component """     
        
        # initialize the component object
        if comp_name is None:
            comp_name = 'Component'
        comp = Component(comp_name, comp_states, comp_transition_matrix)
        self.comp = comp
        self.name = 'Sensed ' + comp.name.capitalize()               

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
        self.extendedHistory += self.extendedHistory + self.comp.history
        self.extendedSensedHistory = self.extendedSensedHistory + self.sensedHistory
        self.comp.reset()
        for sensor in self.sensors:
                sensor.reset()
                sensor.sensorReadings = [self.comp.state]  # reset the sensor readings history and store initial state
        self.sensedHistory = [self.comp.state]             # reset the sensed history of the sensed component and store initial state
        self.state = self.comp.state                       # reset the ground truth state of the component


    def copyHistory(self) -> None:
        """ Copy the history of the component and sensors to the extended histories """
        self.extendedHistory += self.extendedHistory + self.comp.history
        self.extendedSensedHistory = self.extendedSensedHistory + self.sensedHistory
        for sensor in self.sensors:
            sensor.extendedHistory += sensor.history  # Append the history to the extended history
            sensor.extendedReadings += sensor.sensorReadings  # Append the sensor readings to the extended readings
            
        # remove history before maintenance, but dont reset the component or sensors
            sensor.sensorReadings = [self.comp.state]        
        self.sensedHistory = [self.comp.state]             
        self.state = self.comp.state                       

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
        ax.set_title( self.name + ' History')
        # ax.xticks(range(len(self.history)), [f'{i}h' for i in range(len(self.history))], rotation=45) # make x ticks for every hour
        ax.set_xticks(range(0, len(self.comp.history), 5), [f'{i}h' for i in range(0, len(self.comp.history), 5)], rotation=45)   # make x ticks for every 5 hours
        ax.set_xlabel('Time Step')
        ax.set_xlim(0, len(self.comp.history))
        ax.set_yticks(list(self.comp.states.keys()))
        ax.set_yticklabels(list(self.comp.states.values()))
        ax.set_ylabel('State')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  fancybox=True, shadow=True, ncol=5)
        plt.grid()
        plt.show()

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
        plt.show()

        
    def printHistory2Excel(self, filename: str = 'sensedComp_history.xlsx', worksheet = None ) -> None:
        """ 
        This function is used to print the history of the sensed component to an excel file. 
        Each sensed component has one page with its true states, sensor states and sensed states.         
        """
    
        # determining necessary columns for the worksheet
        truth_state_col = 2            # column letter for truth state
        sensed_state_col = 3 + self.n  # column letter for sensed state      
        f1_col = 4 + self.n * 2         # 1 column over from final sensor reading
        f2_col = 5 + self.n * 2         # 2 columns over from final sensor reading

        # add to the workbook using xlsxwriter
        with xlsxwriter.Workbook(filename) as workbook:

            # if no worksheet is provided, create a new workbook and worksheet
            if worksheet is None:
                worksheet = workbook.add_worksheet(self.name) 

            # loop through data points and add them to the worksheet
            n_data = len(self.extendedHistory) # number of data points in the extended history
            for i in range(n_data):
                
                # add time step
                addTimeSteps(workbook, worksheet, i)  # add time step to the first column

                # add truth data starting at the second column
                truth_data = [self.extendedHistory[i]] + [self.sensors[j].extendedHistory[i] for j in range(self.n)]
                if i == 0:
                    sensor_headers = ['Sensor ' + str(i+1) + ' Truth State' for i in range(self.n)]
                    truth_headers = ['Comp Truth State'] + sensor_headers
                    addTruth(workbook, worksheet, i, truth_data, truth_headers)   # add the truth values starting at the second column
                else:
                    addTruth(workbook, worksheet, i, truth_data)

                # add sensed data after truth data
                sensed_data = [self.extendedSensedHistory[i]] + [self.sensors[j].extendedReadings[i] for j in range(self.n)]
                if i == 0:
                    sensor_readings_headers = ['Sensor ' + str(i+1) + ' Reading from Comp' for i in range(self.n)]
                    sensed_headers = ['Sensed State'] + sensor_readings_headers
                    addSensed(workbook, worksheet, i, sensed_data, sensed_headers)   # add the sensed values starting at the second column
                else:
                    addSensed(workbook, worksheet, i, sensed_data)

                # add formula to chech if sensed state matches the truth state
                addUnsensedFailureFormula(workbook, worksheet, i, truth_state_col, sensed_state_col, f1_col, n_data)  # add formula to check if sensors are working
                
                # add formula to check if the sensors are mostly working
                addSensorFailureFormula(workbook, worksheet, i, truth_state_col, f2_col, n_data, self.n)  # add formula to check if the sensed state matches the truth state
            
            # format the sheet for better readability
            finalFormatting(worksheet, self.n) 
                