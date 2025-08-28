'''
    1. Can increased sensor accuracy or number of sensors offer better system availability and reliability then higher levels of redundancy?
		a. Does the length of the mission affect the answer to this question?
		b. How does variance of component failure affect these results? 
'''

from shipClass import Ship


class Q1_Simulator(): 

    '''
        Initialize a ship and identify its frequently failing components 
    '''

    def __init__(self, init_ship_excel):
        self.ship = Ship(init_ship_excel)   # defualts in a repairable manned ship
        self.freq_fail_parts = self.ship.identify_freq_fail_parts()


    def identify_freq_fail_parts(self):
        lowest_MTTFs = [float('inf')] * 3   # list to store the three lowest MTTFs
        freq_fail_parts = []                # list to store the three most frequently failing parts

        # add the three lowest MTTFs
        for i in range(3):
            min_MTTF = float('inf')
            min_comp = None

            for system in self.ship.systems.values():
                for comp in system.components:
                    if comp.MTTF < min_MTTF and comp not in freq_fail_parts:
                        min_MTTF = comp.MTTF
                        min_comp = comp

            if min_comp is not None:
                freq_fail_parts.append(min_comp)

        return freq_fail_parts
