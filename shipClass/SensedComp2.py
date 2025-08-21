from shipClass.Component import Component
from shipClass.Sensor2 import Sensor

import matplotlib.pyplot as plt

class SensedComp():

    """ A collection of functions for a component with attached sensors"""

    def __init__(self, component: Component, sensors: list[Sensor]):
        self.component = component
        self.sensors = sensors

# -------------------- Simulation Functions -----------------------------
    def simulate(self, number_of_steps = 1):
        for i in range(number_of_steps):
            self.component.simulate(1)
            for sensor in self.sensors:
                sensor.read(self.component.state) # allow the sensor to read the component state

# ---------------------- Plotting Functions -----------------------------
    def plotHistory(self):
        ax= self.component.plotHistory()

        for sensor in self.sensors:
           sensor.plotReadings(ax)  
        
        plt.legend()
        plt.show()
        