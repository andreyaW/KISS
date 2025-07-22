""" 
This class is used to simulate a manned ship subject to degradation over time and maintenance actions (CM and PM).
"""

from shipClass.Ship import Ship

class mannedShip(Ship):

    def __init__(self) -> None:
        '''
        param systems: A list of System objects representing the systems on the ship.
        '''
        unmanned = False

                