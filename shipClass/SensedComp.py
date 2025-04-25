from shipClass.Component import Component
from shipClass.Sensor import Sensor
from utils.helperFunctions import find_mode, idx2letter

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
        
    def __init__(self, comp_states: dict[int: str] = {0: 'Failed', 
                                                      1: 'Working'}, 
                 comp_transition_matrix: list[list[float]]=[[1.0, 0.0], 
                                                            [0.02, 0.98]],  
                 sensor_states: dict[int: str] = {0: 'Failed', 
                                                  1: 'Working'}, 
                 sensor_transition_matrix: list[list[float]] = [[1, 0],
                                                                [0.15, 0.85]], 
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


        
    def printHistory2Excel(self, filename: str = 'sensedComp_history.xlsx', worksheet = None ) -> None:
        """ 
        This function is used to print the history of the sensed component to an excel file. 
        Each sensed component has one page with its true states, sensor states and sensed states.         
        """
        # create headers for the output data 
        sensor_headers = ['Sensor ' + str(i+1) for i in range(self.n)]
        headers = ['Time Step', 'Truth State'] + sensor_headers + ['Sensed State', "Are Sensors Working?", "Did Sensed State Match Truth State?"]

        # determining necessary column letters for the worksheet
        truth_state_col = idx2letter(2)            # column letter for truth state
        sensed_state_col = idx2letter(3 + self.n)  # column letter for sensed state      
        sensor_cols = [idx2letter(i+3) for i in range(self.n)]  # columns for sensor states        
        
        f1_col = idx2letter(2 + self.n + 2)        # column 2 over from the sensed state
        f2_col = idx2letter(2 + self.n + 3)        # column 3 over from the sensed state

        with xlsxwriter.Workbook(filename) as workbook:

            # if no worksheet is provided, create a new workbook and worksheet
            if worksheet is None:
                worksheet = workbook.add_worksheet(self.name) 

            # write the headers in the first row
            cell_format = workbook.add_format()
            cell_format.set_text_wrap()
            worksheet.write_row(0, 0, headers, cell_format)
            
            # loop through all data and add it to each row of the worksheet
            for i in range(len(self.extendedHistory)):
                                
                # add truth state, sensor states and sensed state to the row
                sensor_data = [self.sensors[j].extendedHistory[i] for j in range(self.n)]
                data = [i, self.comp.extendedHistory[i]] + sensor_data + [self.extendedSensedHistory[i]]
                worksheet.write_row(i+1, 0, data, )
                             
                # adding a formula to chek if sensors are working
                row = i + 2     # formulas consider data which starts from row 2 
                if self.n == 1: 
                    # copy sensor state from colomn C
                    f1_sensors_working = f'={sensor_cols[0]}{row}' # can take the first sensor state as the only sensor is present
                    worksheet.write_formula(f'{f1_col}{row}', f'={sensor_cols[0]}{row}')        
                else: 
                    f1_sensors_working = f'=MODE(C{row}:{sensor_cols[-1]}{row})'  # formula to check if all sensors are working
                worksheet.write_formula(f'{f1_col}{row}', f1_sensors_working)        
       
                # adding a formula to check if the sensed state matches the truth state
                f2_check_missed_failure = f'=IF({truth_state_col}{row}={sensed_state_col}{row}, 1, 0)'  # formula to check if the sensed state matches the truth state
                worksheet.write_formula(f'{f2_col}{row}', f2_check_missed_failure)                
           
            # add conditional formating to this column to highlight the cells
            worksheet.conditional_format(f'{f1_col}2:{f1_col}{row}', 
                                        {'type': '2_color_scale',
                                            'min_color': '#FD0000',  # red
                                            'max_color': '#00FD00'}) # green

            worksheet.conditional_format(f'{f2_col}2:{f2_col}{row}', 
                                        {'type': '2_color_scale',
                                            'min_color': '#FD0000',  # red
                                            'max_color': '#00FD00'}) # green

            # increase column width for better readability
            for i in range(len(headers)):
                worksheet.set_column(i, i, 11.5)
                