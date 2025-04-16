""" 
This class is used to simulate a ship object subject to degradation over time and maintenance actions.
"""

from shipClass import shipClass

import pandas as pd

class shipSimulator():

    def __init__(self, shipType : str, simulationLength: int) -> None:   
        
        '''
        param shipClass: The class of the ship object to be simulated. (manned or unmanned)
        param simulationLength: The length of the simulation in hours.
        '''
        
        self.shipType = shipType
        self.simulationLength = simulationLength
        
        
        
    def setupSimulation(self):
        
        '''
        This method sets up the simulation by creating the ship object and initializing any necessary variables.
        '''
        
        # Create the ship object using the provided class
        if self.shipType == 'manned':
            self.ship = shipClass.mannedShip()
        elif self.shipType == 'unmanned':
            self.ship = shipClass.unmannedShip()
        else:
            raise ValueError("Invalid ship type. Please choose 'manned' or 'unmanned'.")
        
        # Initialize any other necessary variables or data structures here
        # self.simulationData = []
       
       
        
        
    def simulate(self, run_time: int):
        """ sill simulate a manned or unmanned vessel and keep track of maintenane actions performed"""
        
        # simulation loop
        time_step = 0          
        while time_step != run_time:
            
            # simulate the ship's systems
            for system in self.ship.systems:
                system.simulate(1)  # simulate each system for 1 hour       
            
                # determine if maintenance is needed to bring the system back to a healthy state
                if system.state == 0 :
                    
            time_step += 1          # each step = 1 hour
    