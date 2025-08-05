""" 
This class is used to simulate an unmanned ship subject to degradation over time and maintenance actions (PM only).
"""

from shipClass.Ship import Ship
from shipClass.System import System
from utils.maintenanceFunctions import periodicMaintenance

import pandas as pd
import openpyxl


class unmannedShip():
            
    def __init__(self, vessel:Ship)-> None:
        '''
        param systems: A list of System objects representing the systems on the ship.
        '''

        self.vessel = vessel
        self.name = vessel.name



    def defineSystemsfromExcelData(excel_file, systems_names, list_of_system_components):
            
        data= pd.read_excel("AuxilaryPropulsionPlant_Reliability_Availability_Data.xlsx")
        print(data)

        # defining the systems as they are shown in the image above
        transmission_sys = [2, 3, 4]
        engine_sys = [8, 9, 10, 11, 12, 6, 0, 1]
        #fuel_sys = [(5, 6), 7] *2
        # twin_engine_sys = [fuel_sys , (engine_sys_1, engine_sys_2), transmission_sys]



    def conductPM(self, timeStep)-> None:
        '''
        This method conducts periodic maintenance on the ship's systems.
        It iterates through each system and performs maintenance actions as needed.
        '''
        # Conduct periodic maintenance on each system
        for sys in self.vessel.systems:
            periodicMaintenance(sys)

        