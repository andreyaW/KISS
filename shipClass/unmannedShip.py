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


    def generatePMPeriod(self):
        '''add a function to make the periodic maintenance period have an average and distribution'''
        return 10



    def conductPM(self, system):

        PM_Period = self.generatePMPeriod()

        # determine which comps need to be fixed
        for comp in system.comps:
            if comp.comp.state == 0:
                # making the components being repaired reflect repair time
                repair_time = [-1 for i in range(PM_Period)]
                comp.comp.history += repair_time
                comp.sensedHistory+= repair_time
                comp.reset()                        # good as new repair after repair period ends

            # leave the component not being repaired in thier current state until PM is done
            else:
                idle_time = [comp.comp.state for i in range(PM_Period)]
                comp.comp.history+= idle_time
                comp.sensedHistory+= idle_time
                comp.copyHistory()
                
        return PM_Period

          
