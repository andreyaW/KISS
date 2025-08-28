""" 
This class is used to simulate a manned ship subject to degradation over time and maintenance actions (CM and PM).
"""

from shipClass.Ship import Ship

class mannedShip(Ship):

    def __init__(self, name, ship_data_file)-> None:
        """
        This class is used to simulate an manned ship subject to degradation over time and maintenance actions (CM and PM).
            Parameters
            ----------
            name: str
                The name of the ship.
                
            ship_data_file: str
                The path to the Excel file containing ship data.
        """
        
        self.repairable = True # This ship is manned so minor failures can be repaired
        super().__init__(name, excel_file=ship_data_file, repairable=self.repairable)
