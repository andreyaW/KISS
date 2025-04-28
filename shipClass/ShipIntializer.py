""" this class is used to initialize the ship class for simulation"""

from shipClass.Ship import Ship
from shipClass.System import System


class ShipInitializer:

    def __init__(self, ship_class, ship_name, ship_type):
        self.ship_name = ship_name
        self.ship_type = ship_type
        
        
    def add_systems(self, comp_attributes, parallels):
        
        """ this method is used to add systems to the ship class"""
        
        for comp_attributes in :
            system = System(system, comp_attributes, parallels)
            self.ship_class.add_system(system)
        
        # for system in self.systems:
        #     system.add_system(comp_attributes, parallels)
        
        
        
    