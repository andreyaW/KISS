'''
    1. Can increased sensor accuracy or number of sensors offer better system availability and reliability then higher levels of redundancy?
		a. Does the length of the mission affect the answer to this question?
		b. How does variance of component failure affect these results? 



        # Functions needed to answer the questions
            1. identify_freq_fail_parts() - 
                able to identify which components will need increased redundancy or more sensors
                *could have a unit test since I know the answer to this
            2. assess_ship_RAM()- 
                determine the ships RAM performance for a given mission profile
            3. assess_sensor_impact() -
                able to assess the impact of sensor accuracy and quantity on system reliability
            4. vary_mission_length 
                will simulate the ship for various mission lengths 
            5. output_statistics
                send simulation data to an output file
            6. increase_sensor_accuracy
                add assess the impact of increased sensor accuracy on system reliability
            7. increase_redundancy
                add and assess the impact of increased redundancy on system reliability
'''
from shipClass.SeriesComps import SeriesComps

class Q1_Simulator(): 

    '''
        Initialize a ship and identify its frequently failing components 
    '''

    def __init__(self, sensedShip):
        self.sensed_ship = sensedShip
        self.shipVariations = []

    def identify_freq_fail_parts(self):

        ship = self.sensed_ship.ship
        freq_fail_parts = {}

        # store every component into a dictionary with its name and MTTF
        for system in ship.systems.values():
            for comp in system.comps:

                if type(comp) is SeriesComps:
                    for comps in comp.comps:
                        freq_fail_parts[comps.name] = comps.MTTF
                else:
                    freq_fail_parts[comp.name] = comp.MTTF

        # Sort the dictionary by values from lowest to highest
        sorted_fails = sorted(freq_fail_parts.items(), key=lambda item: item[1])

        # Return the three components with the lowest MTTF
        freq_fail_parts = dict(sorted_fails[:3]) 
        return freq_fail_parts
    

    def increase_ship_redundancy(self):
        self.identify_freq_fail_parts()

        # Implement redundancy increase logic here
        pass


    

    def increase_sensor_accuracy(self):
        self.identify_freq_fail_parts()

        # Implement sensor accuracy increase logic here
        pass

    # def vary_mission_length(self, mission_lengths):

    #     # Simulate the ship for various mission lengths
    #     for length in mission_lengths:
    #         print(f"Simulating mission length: {length}")
    #         self.run_simulation(mission_length=length)


    # def run_simulation(self, mission_length):
    #     pass 