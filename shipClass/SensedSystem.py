from shipClass.System import System
from shipClass.Sensor_basic import Sensor
from shipClass.SensedComp import SensedComp
from utils.helperFunctions import SolveStructureFunction

import matplotlib.pyplot as plt

class SensedSystem(System):
    ''' a class which holds the system class and also attaches sensors to each component of the system to get readings 
    '''
    def __init__(self, system: System, number_of_sensors: list[int] = None):
        self.system = system        
        self.sensedState = self.system.state
        self.history = [self.sensedState]
        self.sensedComps = []

        # if the number of sensors per component is not specified, add defualts
        if number_of_sensors is None:
            self.number_of_sensors = [3 for comp in self.system.comps]
        else: 
            self.number_of_sensors = number_of_sensors
        self.attach_sensors()

    def attach_sensors(self):
        comps = self.system.comps
        for i, comp in enumerate(comps):
            sensors = [Sensor() for _ in range(self.number_of_sensors[i])] # attaching good sensors (default)
            sensed_comp = SensedComp(comp, sensors)
            self.sensedComps.append(sensed_comp)

    def simulate(self, time_step):
        sensedComps = self.sensedComps
        for i in range(time_step):
            for sensed_comp in sensedComps:
                sensed_comp.simulate(1)

            # update the system truth state
            self.system.update_state()  

            # update the system sensed state
            self.sensedState = SolveStructureFunction(sensedComps, self.system.parallels, sensed=True)
            self.history.append(self.sensedState)


    def plotHistory(self, plot_comp_history = False, return_ax = False):
        ''' plot the history of the sensed system '''
        # plot the true history of the system
        ax = self.system.plotHistory(plot_comp_history, return_ax=True)

        # plot the sensed history of the system
        ax.plot(self.history, marker=',', label='Sensed', linestyle='--', color='orange')

        # add updated legend
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                fancybox=True, shadow=True, ncol=5)
        plt.show()

        if return_ax:
            return ax

    # def plotHistory(self, plot_comp_history = False):
    #     return super().plotHistory(plot_comp_history)