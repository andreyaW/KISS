from shipClass.SensedSystem import SensedSystem
from shipClass.Ship import Ship

class SensedShip():
    def __init__(self, ship: Ship):
        self.ship = ship
        self.sensedSystems = []

    def attachSensors(self):
        for shipSystems in self.ship.systems:
            sensedSystem = SensedSystem(shipSystems)
            self.sensedSystems.append(sensedSystem)

    def simulate(self, time_step):
        pass

    def plotHistory(self):
        pass




        