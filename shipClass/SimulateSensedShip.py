from shipClass.Ship import Ship
from shipClass.SensedShip import SensedShip

import numpy as np

# -------- Ship Initialization Functions -----------------------------
def initialize_sensed_aux_ship(np_rng_num = 0, sensors = None):

    from shipClass.Ship import Ship
    from shipClass.SensedShip import SensedShip

    aux_ship = Ship(name="Auxiliary Ship",
                    excel_file="AuxilaryPropulsionPlant_Reliability_Availability_Data.xlsx",
                    repairable=False,
                    np_rng_num=np_rng_num)

    if sensors is not None:
        sensed_aux_ship = SensedShip(ship=aux_ship, sensors=sensors)
    else: 
        sensed_aux_ship = SensedShip(ship=aux_ship)

    return sensed_aux_ship

# -------- Simulation with Spare Parts Logic -----------------------------
# Notes for what's left to implement:
    # only repair a system if it is required for ship operation
    # queue repairs if a system is in alarm state
    # repairs should follow a MTTR distribution not be instantaneous
    # once spare parts inventory reaches a threshold, more spares should be ordered (with lead time)
    # track false alarms and false failures separately
    # track which systems have the greatest downtime

# optional: could have a different lead time and ordering cost for different types of spare parts

def simulateWithSpareParts(sensedShip, time_steps: int, number_of_spares: int):
    """ Simulate the ship with spare parts logic """
    
    count_unrepairable_fails = 0  # counter for unrepairable failures(i.e. times with no spares left)
    count_false_alarms = 0        # counter for false failure alarms
    
    for t in range(time_steps):

        sensedShip.simulate(1)  # simulate one time step

        # check for failed systems and repair with spares if available
        for sensedSystem in sensedShip.sensedSystems:
            if sensedSystem.sensedState == 0:  # if the system is sensed as failed
                
                # if spares are available, use one to repair the system
                if number_of_spares > 0:
                    false_alarm, sensedSystem = queueRepair(sensedSystem, number_of_spares)  # queue repair for the system
                    count_false_alarms += false_alarm  # increment false alarm counter if applicable
                else:
                    # if no spares available, order new part and delay repair 
                    # *** "order part" logic goes here later***
                    count_unrepairable_fails += 1
                    pass
            else:
                continue  # system is operational, do nothing
    
    print(f"Total unrepairable failures due to lack of spares: {count_unrepairable_fails}")
    print(f"Total false failure alarms: {count_false_alarms}")


# -------- Spare Parts Management Functions -----------------------------
def queueRepair(sensedSystem, number_of_spares):
    """ Queue repairs for failed systems """

    # determine if the system is actually failed or if it's a false alarm
    system = sensedSystem.system

    if system.state == 0:  # system is actually failed
        # use a spare part to repair the system
        number_of_spares -= 1  # decrement the number of spares available

        # simulate repair time (for simplicity, we assume immediate repair here)
        system.reset()  # replace with a spare (reset the system)

        return 0, sensedSystem  # return 0 indicating a real failure repair
    else:
        # false alarm, no action needed
        return 1, sensedSystem

    
    # # determine which components need repair
    # comp_states = np.array([comp.state for comp in system.comps])
    # failed_indices = np.where(comp_states == 0)[0]  # indices of failed components

    # num_failed = len(failed_indices)
    # if num_failed == 1:
    #     comp_to_repair = system.comps[failed_indices[0]]
    #     avg_repair_time = comp_to_repair.MTTF

    #     time_until_repair = np.floor(np.random.lognormal(mean=np.log(avg_repair_time), sigma=0.5))

    #     # ensure the repair time is at least 1 and at most 3*avg_repair_time
    #     time_until_repair = max(1, min(time_until_repair, 3 * avg_repair_time))
    #     repair_time = time_until_repair

    # elif num_failed > 1:
    #     # need to add priority repairs logic based on some criteria (e.g., criticality, repair time)
    #     # for simplicity, we will just repair the first failed component here
    #     pass 
    # # need to add repair time logic here later***

        



def orderMoreSpares(self, number_of_spares: int):
    """ Order more spare parts when inventory reaches a certain threshold """

    # Order more spare parts logic goes here later*** 
    pass