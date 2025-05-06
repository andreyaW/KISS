""" 
This class is used to simulate a ship object subject to degradation over time and maintenance actions.
"""

from shipClass import shipClass
from shipClass.System import System


class shipSimulator():

    def __init__(self, shipType : str, systems: list[System] self.parallels, simulationLength: int) -> None:   
        
        '''
        param shipClass: The class of the ship object to be simulated. (manned or unmanned)
        param simulationLength: The length of the simulation in hours.
        '''
        
        self.shipType = shipType
        self.simulationLength = simulationLength
        self.systems = systems
        
        
    def setupSimulation(self, ):
        
        '''
        This method sets up the simulation by creating an appropriate ship object based on the provided class.
        '''
        
        # Create the ship object using the provided class
        if self.shipType == 'manned':
            self.ship = shipClass.mannedShip(self.systems)

        elif self.shipType == 'unmanned':
            self.ship = shipClass.unmannedShip(self.systems)
        else:
            raise ValueError("Invalid ship type. Please choose 'manned' or 'unmanned'.")
        
        # Initialize any other necessary variables or data structures here
        # self.simulationData = []
       


    
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
    