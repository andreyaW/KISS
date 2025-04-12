""" 
This class is used to simulate a manned ship subject to degradation over time and maintenance actions (CM and PM).
"""

from shipClass.Ship import Ship
from shipClass.Maintenance import correctiveMaintenance
from shipClass.Maintenance import preventativeMaintenance

class mannedShip(Ship):

    def __init__(self, systems:list[System]) -> None:
        '''
        param systems: A list of System objects representing the systems on the ship.
        '''
        
        self.systems = systems

# ---------------------- Simulation of Object  ----------------------       

    def simulate(): 
        pass