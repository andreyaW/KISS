""" 
This class is used to a ship object (parent class). Different types of ships (manned and unmanned) will inherit from this class.
"""

from shipClass.System import System
from shipClass.Maintenance import Maintenance

class Ship:

    def __init__(self, systems: list[System]) -> None:
        '''
        param systems: A list of System objects representing the systems on the ship.
        '''
        
        self.systems = systems
        self.maintenanceTimes = {}  # List to keep track of maintenance times for each system

        
    def simulate(self, num_hours: int) -> None: 
        '''
        This method simulates the ship object by iterating through each system and performing maintenance actions as needed.
        '''
        
        # Iterate through each system and update it, then perform maintenance actions as needed
        for hours in range(num_hours): 
            for system in self.systems:
                system.simulate(1)  # Simulate the system for 1 hour
            
