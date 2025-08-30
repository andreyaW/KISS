'''
    1. Can increased sensor accuracy or number of sensors offer better system availability and reliability then higher levels of redundancy?
		a. Does the length of the mission affect the answer to this question?
		b. How does variance of component failure affect these results? 



        # Functions needed to answer the questions
            1. identify_freq_fail_parts() - 
                able to identify which components will need increased redundancy or more sensors
                *unit test 
                    auxillary ship lowest rel parts = {'Lube Oil Pump': np.int64(4000), 'Fuel Oil Pump': np.int64(5500), 'Fuel Oil Booster Pump': np.int64(5500)}
          
            2.  increase_redundancy
                add and assess the impact of increased redundancy on system reliability
                *unit test- Aux ship fuel system 
                    start with no redundancy and add the redundancy to the fuel motor + pump first then to the purifier to arrrive at the system presented in Lawrence Stone thesis. 

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
            7. 
'''
from shipClass.SeriesComps import SeriesComps
from shipClass.SensedShip import SensedShip
from shipClass.System import System

class Q1_Simulator(): 

    '''
        Initialize a ship and identify its frequently failing components 
    '''

    def __init__(self, sensedShip):
        self.sensed_ship = sensedShip
        self.shipVariations = []

    def identify_freq_fail_parts(self, obj):

        # determine if the object is a SensedShip or System
        if isinstance(obj, SensedShip): 
            systems= obj.ship.systems.values()
        elif isinstance(obj, System):
            systems = [obj]

        # grab all MTTF values for the components in the obj
        freq_fail_parts = {}
        for system in systems:
            for comp in system.comps:
                freq_fail_parts[comp] = comp.MTTF

        # Sort the failure times dictionary from lowest to highest
        sorted_fails = sorted(freq_fail_parts.items(), key=lambda item: item[1])

        # Return the three components with the lowest MTTF
        freq_fail_parts = dict(sorted_fails[:3]) 
        return freq_fail_parts


    def increase_redundancy(self, obj):

        # identify the lowest reliability parts
        low_rel_parts = self.identify_freq_fail_parts(obj)

        # Increase redundancy for the identified parts
        
        # system logic
        if isinstance(obj, System):
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