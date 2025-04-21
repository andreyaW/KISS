""" this class is used to initialize the ship class for simulation"""

from shipClass import ShipClass


    def create_ship(self):
        return ShipClass(
            ship_class=self.ship_class,
            ship_name=self.ship_name,
            ship_type=self.ship_type,
            ship_length=self.ship_length,
            ship_width=self.ship_width,
            ship_draft=self.ship_draft,
            ship_speed=self.ship_speed
        )


class ShipInitializer:
    def __init__(self, ship_class, ship_name, ship_type):
        self.ship_class = ship_class
        self.ship_name = ship_name
        self.ship_type = ship_type
        self.systems = systems
        
        
    def add_systems(self, comp_attributes, parallels): ):
        
        for vals in comp_attributes:
            
        
        
        self.systems = systems