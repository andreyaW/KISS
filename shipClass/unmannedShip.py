""" 
This class is used to simulate an unmanned ship subject to degradation over time and maintenance actions (PM only).
"""

from shipClass.Ship import Ship
from shipClass.System import System
from shipClass.Maintenance import periodicMaintenance

class unmannedShip():
            
    def __init__(self, vessel:Ship)-> None:
        '''
        param systems: A list of System objects representing the systems on the ship.
        '''

        self.vessel = vessel
        self.name = vessel.name

    def conductPM(self, timeStep)-> None:
        '''
        This method conducts periodic maintenance on the ship's systems.
        It iterates through each system and performs maintenance actions as needed.
        '''
        # Conduct periodic maintenance on each system
        for sys in self.vessel.systems:
            periodicMaintenance(sys)

        