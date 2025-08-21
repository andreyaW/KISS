from shipClass.System import System
from shipClass.Sensor2 import Sensor
from shipClass.SensedComp2 import SensedComp

class SensedSystem(System):

    def __init__(self, system: System):
        self.system = system
        self.sensedComps = []

    def attach_sensors(self, number_of_sensors):

        comps = self.system.components

        for comp in comps:
            sensors = [Sensor() for _ in range(number_of_sensors)]
            sensed_comp = SensedComp(comp, sensors)
            self.sensedComps.append(sensed_comp)


    # def initializeSystem(self, repairable = False):
    #     return super().initialize(repairable)