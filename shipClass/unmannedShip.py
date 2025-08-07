""" 
This class is used to simulate an unmanned ship subject to degradation over time and maintenance actions (PM only).
"""

from shipClass.Ship import Ship
from shipClass.System import System
from utils.maintenanceFunctions import periodicMaintenance

import pandas as pd
import openpyxl


class unmannedShip(Ship):
            
    def __init__(self)-> None:
        '''
        param systems: A list of System objects representing the systems on the ship.
        '''
        super.vesselType = "unmanned"

        # super.__init_subclass__()
        
    def conductPM(self, timeStep)-> None:
        '''
        This method conducts periodic maintenance on the ship's systems.
        It iterates through each system and performs maintenance actions as needed.
        '''
        # Conduct periodic maintenance on each system
        for sys in self.vessel.systems:
            periodicMaintenance(sys)

        