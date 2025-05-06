""" 
This class is used to simulate an unmanned ship subject to degradation over time and maintenance actions (PM only).
"""

from shipClass.Ship import Ship
from shipClass.System import System
from shipClass.Maintenance import periodicMaintenance

import numpy as np

class unmannedShip(Ship):
            
    def __init__(self, name, systems: list[System], parallels=None) -> None:
        '''
        param systems: A list of System objects representing the systems on the ship.
        '''
        super().__init__(name, systems, parallels)
        self.perodic_maintenance_period = 10    # hours
        self.maintenance_delay = 5



          
