""" 
This class is used to simulate a manned ship subject to degradation over time and maintenance actions (CM and PM).
"""

from shipClass.Ship import Ship

class mannedShip(Ship):

    def __init__(self)-> None:
        '''
        param systems: A list of System objects representing the systems on the ship.
        '''
        self.unmanned = False # This ship is manned
        super().__init_subclass__(unmanned=self.unmanned) # initialize the ship and its systems as unmanned


    