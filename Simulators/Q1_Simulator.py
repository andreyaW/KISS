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

import copy

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


    def increase_sys_redundancy(self, sys, num_parts_to_add: int= 3):

        # identify the lowest reliability parts
        low_rel_parts = list(self.identify_freq_fail_parts(sys))

        # identify the idx of the low rel parts in the original system
        low_rel_parts_idx = [sys.comps.index(part) for part in low_rel_parts]

        # stop when we have added the desired number of redundant parts
        stop_case = len(low_rel_parts) - num_parts_to_add

        # Increase redundancy for the identified parts and save each to a new ship variation
        while len(low_rel_parts_idx) != stop_case:

            # Create a deep copy of the systems components
            updated_comps = copy.deepcopy(sys.comps)

            # find the components location in the system 
            comp_index = low_rel_parts_idx[0]

            # add a copy of it to the components list
            updated_comps.insert(comp_index+1, low_rel_parts[0])

            # update the indices of the lowest rel parts
            low_rel_parts_idx = [x+1 if x >= comp_index+1 else x for x in low_rel_parts_idx]

            # update the indices present in the parallels list
            if sys.parallels is not None: 
                updated_parallels = copy.deepcopy(sys.parallels)
                for i, tup in enumerate(updated_parallels):
                    updated_parallels[i] = tuple(x+1 if x > comp_index+1 else x for x in tup)
            else:
                updated_parallels = []

            # determine if the component was in a parallel set, and update parallels accordingly
            parallels_flattened = [item for tup in updated_parallels for item in tup]
            if comp_index+1 in parallels_flattened:

                # determine which tuple the comp_index was in and add it again
                for i,tup in enumerate(updated_parallels):
                    if comp_index+1 in tup:
                        addition = (comp_index+2, )
                        tup = tup + addition
                        updated_parallels[i] = tup
                        break
            else: 
                updated_parallels.append((comp_index+1, comp_index+2))
                print(updated_parallels)

            # initialize a new system with the updated comps
            new_system = System(name=sys.name, 
                                comps=updated_comps, 
                                parallels=updated_parallels, 
                                repairable=self.sensed_ship.ship.repairable)

            # replace the old system and save it to a new ship variation
            shipVariation = copy.deepcopy(self.sensed_ship.ship)
            shipVariation.systems[sys.name] = new_system
            self.shipVariations.append(SensedShip(shipVariation))

            # replace the system (sys) with the new system and move to the next part
            sys = new_system
            low_rel_parts_idx.pop(0)



    def increase_ship_redundancy(self):
        # identify the lowest reliability parts
        low_rel_parts = list(self.identify_freq_fail_parts(self.sensed_ship))

        # determine which systems the low reliability part is in
        low_rel_parts_systems = {}
        for part in low_rel_parts:
            for sys in self.sensed_ship.ship.systems.values():
                if part in sys.comps:
                    low_rel_parts_systems[part] = sys

        # add redundancy to the identified systems
        for part, sys in low_rel_parts_systems.items():
            print('\n Adding', part.name, 'in:', sys.name)
            self.increase_sys_redundancy(sys, 1)


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