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

    def simulate(self, num_hours: int) -> None:
        '''
        This method simulates the ship object by iterating through each system and performing maintenance actions as needed.
        '''
        for i in range(num_hours): 
            
            # Update the state of all the systems
            super().simulate(1) # call the parent class simulate method
        
            # Perform maintenance actions as needed
            for system in self.systems:

                # perform periodic maintenance on the systems at the specified interval
                if np.mod(len(system.history), self.perodic_maintenance_period) == 0:
                    system = periodicMaintenance(system,self.maintenance_delay)

            
            
