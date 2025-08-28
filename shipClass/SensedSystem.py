from shipClass.System import System
from shipClass.Sensor2 import Sensor
from shipClass.SensedComp2 import SensedComp
from utils.helperFunctions import SolveStructureFunction

import matplotlib.pyplot as plt

class SensedSystem(System):
    ''' a class which holds the system class and also attaches sensors to each component of the system to get readings 
    '''
    def __init__(self, system: System, number_of_sensors: list= None):
        self.system = system
        self.sensedComps = []
        self.sensedState = self.system.state
        self.history = [self.sensedState]
        
        # if the number of sensors per component is not specified, add defualts
        if number_of_sensors is None:
            self.number_of_sensors = [3 for comp in self.system.comps]

    def attach_sensors(self):
        comps = self.system.comps
        for i, comp in enumerate(comps):
            sensors = [Sensor() for _ in range(self.number_of_sensors[i])]
            sensed_comp = SensedComp(comp, sensors)
            self.sensedComps.append(sensed_comp)


    def simulate(self, time_step):
        sensedComps = self.sensedComps
        for i in range(time_step):
            for sensed_comp in sensedComps:
                sensed_comp.simulate(1)

            # additional logic for the overall system simulation
            print(self.system.parallels)
            self.sensedState = SolveStructureFunction(sensedComps, self.system.parallels, sensed=True)
            self.history.append(self.sensedState)


    def plotHistory(self, plot_comp_history = False):
        ''' plot the history of the sensed system '''
        # plot the true history of the system
        ax = self.system.plotHistory(plot_comp_history)

        # plot the sensed history of the system
        ax.step(range(len(self.history)), self.history, where='post', label='Sensed System State', linestyle='--', color='orange')
        ax.legend()
        plt.show()

        return ax
    # def plotHistory(self, plot_comp_history = False):
    #     return super().plotHistory(plot_comp_history)