""" 
This class is used to simulate a ship object subject to degradation over time and maintenance actions.
"""

from shipClass.Ship import Ship
from shipClass.unmannedShip import unmannedShip
from shipClass.mannedShip import mannedShip

import numpy as np

class ShipSimulator():

    def __init__(self, ship: Ship, # intialized ship with systems of components 
                 vesselType:str, # unmanned or manned 
                 simulationLen : int = 100)-> None:
        
        '''
        param shipClass: The class of the ship object to be simulated. (manned or unmanned)
        param simulationLength: The length of the simulation in hours.
        '''
        self.shipType = vesselType.lower()
        self.vessel = self.setupSimulation(ship, vesselType)
        self.simulationLength = simulationLen
 
    def setupSimulation(self, ship, vesselType):
        
        '''
        This method sets up the simulation by creating an appropriate ship object based on the provided class.
        '''
          
        # Adding considerations to the ship based on its ship Type
        if vesselType == "unmanned":
            ship = unmannedShip(ship)

        elif vesselType == "manned":
            ship = mannedShip(ship)
        else:
            print(vesselType)
            raise ValueError("Invalid vessel type. Please enter 'manned' or 'unmanned'.")
        return ship

    
    def simulate(self) -> None:
        '''
        This method simulates the ship object by iterating through each system and performing maintenance actions as needed.
        '''
        # Start the simulation at time step 0; ship initial state = working
        time_step = 0
        ship = self.vessel

        while time_step < self.simulationLength:
            
            # update the transition matrices of the components using the time_step 
            for sys in ship.systems:
                for comp in sys.comps:
                    comp.updateTransitionMatrix(time_step)

            # simulate the ship for one time step
            ship.simulate(1)

            # check if periodic maintenance must be done
            if np.mod(time_step,self.PM_Interval) ==0 :
                for sys in ship.systems:
                    if sys.state ==0:
                        PM_period = ship.conductPM(sys)
                        # add the maintenance time to the simulation history
                        time_step += PM_period
                    else:
                        pass

            # if manned ship, check for corrective maintenance
            if self.vesselType == "manned":
                for sys in ship.systems:
                    if sys.state == 0:
                        CM_period = ship.conductCM(sys, time_step)   
                    else:
                        pass
                

            time_step +=1       # add one immediately to avoid starting with PM at step 0
