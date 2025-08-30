from shipClass.SensedSystem import SensedSystem
from shipClass.Ship import Ship
from utils.helperFunctions import SolveStructureFunction, set_x_ticks

import matplotlib.pyplot as plt

class SensedShip():
    def __init__(self, ship: Ship, number_of_sensors: list[int] = None):
        self.ship = ship
        self.sensedState = self.ship.state
        self.history = [self.sensedState]
        self.sensedSystems = []

        self.number_of_sensors = number_of_sensors
        if self.number_of_sensors is None:
            self.number_of_sensors = [[3 for i in range((len(shipSystems.comps)))] for shipSystems in self.ship.systems.values()]
        else: 
            self.number_of_sensors = number_of_sensors
        print(self.number_of_sensors)

        self.attach_sensors()

    def attach_sensors(self):
        shipSystems = self.ship.systems.values()
        for i, shipSystem in enumerate(shipSystems):
            sensedSystem = SensedSystem(shipSystem, self.number_of_sensors[i])
            self.sensedSystems.append(sensedSystem)


    def simulate(self, time_step):
        for i in range(time_step):
            for sensedSystem in self.sensedSystems:
                sensedSystem.simulate(1)

            # update the truth state of the ship
            self.ship.update_state()

            # determine the sensed state of the ship
            self.sensedState = SolveStructureFunction(self.sensedSystems, self.ship.parallels, sensed=True)
            self.history.append(self.sensedState)


    def plotHistory(self):
        # Plot the true history of the ship
        ax = self.ship.plotHistory(return_ax=True)

        # Plot the sensed history of the ship
        ax.plot(self.history, marker=',', label='Sensed', linestyle='--', color='orange')

        # add updated legend and show fig
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  fancybox=True, shadow=True, ncol=5)
        plt.show()