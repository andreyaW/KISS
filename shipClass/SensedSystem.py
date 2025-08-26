from shipClass.System import System
from shipClass.Sensor2 import Sensor
from shipClass.SensedComp2 import SensedComp

class SensedSystem(System):

    def __init__(self, system: System, number_of_sensors: list= None):
        self.system = system
        self.sensedComps = []
        
        # if the number of sensors per component is not specified, add defualts
        if number_of_sensors is None:
            self.number_of_sensors = [3 for comp in self.components]

    def attach_sensors(self):

        comps = self.system.components

        for i, comp in enumerate(comps):
            sensors = [Sensor() for _ in range(self.number_of_sensors[i])]
            sensed_comp = SensedComp(comp, sensors)
            self.sensedComps.append(sensed_comp)

    def simulate(self, time_step):
        sensedComps = self.sensedComps
        for sensed_comp in sensedComps:
            sensed_comp.simulate(time_step)

    # def plotHistory(self, plot_comp_history = False):
    #     return super().plotHistory(plot_comp_history)