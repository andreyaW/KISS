""" 
This class is used to simulate a ship object subject to degradation over time and maintenance actions.
"""

from shipClass.Ship import Ship
from shipClass.unmannedShip import unmannedShip
from shipClass.mannedShip import mannedShip

import numpy as np

class ShipSimulator():

    def __init__(self, ship: Ship, shipType:str, 
                simulationLen : int = 100, PM_Interval: float = 10)-> None:
        
        '''
        param shipClass: The class of the ship object to be simulated. (manned or unmanned)
        param simulationLength: The length of the simulation in hours.
        '''

        self.ship = self.setupSimulation(ship, shipType)
        self.simulationLength = simulationLen
        self.PM_Interval = PM_Interval          # how often periodic maintenance should be done


    def setupSimulation(self, ship, shipType):
        
        '''
        This method sets up the simulation by creating an appropriate ship object based on the provided class.
        '''
           
        # Adding considerations to the ship based on its ship Type
        if shipType == "unmanned":
            ship = unmannedShip(ship.name, ship.systems, ship.parallels)
        elif shipType == "manned":
            ship = mannedShip(ship.name, ship.systems, ship.parallels)
        else:
            print(shipType)
            raise ValueError("Invalid ship type. Please enter 'manned' or 'unmanned'.")
        
        # Initialize any other necessary variables or data structures here
        # self.simulationData = []
    
        return ship

    
    def simulate(self) -> None:
        '''
        This method simulates the ship object by iterating through each system and performing maintenance actions as needed.
        '''
        time_step = 0
        ship = self.ship
        while time_step < self.simulationLength:
            
            time_step +=1       # add one immediately to avoid starting with PM at step 0

            # update the transition matrices of the components using the time_step 

            # simulate the ship for one time step
            ship.simulate(1)

            # check if maintenance must be done
            if np.mod(time_step,self.PM_Interval) ==0 :
                for sys in ship.systems:
                    if sys.state ==0:
                        PM_period = ship.conductPM(sys)
                        # add the maintenance time to the simulation history
                        time_step += PM_period
                    else:
                        pass