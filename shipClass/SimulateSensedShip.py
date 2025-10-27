from shipClass.Ship import Ship
from shipClass.SensedShip import SensedShip

import numpy as np

# -------- Ship Initialization Functions -----------------------------
def initialize_sensed_aux_ship(np_rng_num = 0, sensors = None):

    from shipClass.Ship import Ship
    from shipClass.SensedShip import SensedShip

    aux_ship = Ship(name="Auxiliary Ship",
                    excel_file="AuxilaryPropulsionPlant_Reliability_Availability_Data.xlsx",
                    repairable=False,       # repairs should not happen automatically
                    np_rng_num=np_rng_num)

    if sensors is not None:
        sensors = [[sensors for comps in system.comps] for system in aux_ship.systems.values()]
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
    count_repairs = 0             # counter for total repairs made
    for t in range(time_steps):
        # simulate the ship for one time step
        sensedShip.simulate(1)  

        # check for failed systems and repair with spares if available
        for sensedSystem in sensedShip.sensedSystems:

            # if the system is sensed as failed, attempt repair
            if sensedSystem.sensedState == 0:   # if the system is sensed as failed
                
                # if spares are available, queue a repair using one one spare
                if number_of_spares > 0:
                    false_alarm, sensedSystem, num_repairs = queueRepair(sensedSystem, number_of_spares)  # queue repair for the system
                    count_false_alarms += false_alarm  # increment false alarm counter if applicable
                    count_repairs += num_repairs      # increment total repairs counter
                else:
                    # if no spares available, order new part and delay repair 
                    # *** "order part" logic goes here later***
                    count_unrepairable_fails += 1
                    pass

            # if the system is sensed as incipient failure, 
            elif sensedSystem.sensedState == 1: # if the system is sensed as incipient failure
                # *** incipient failure handling logic goes here later ***
                pass
            
            else:
                continue  # system is operational, do nothing
    print(f"Total repairs made: {count_repairs}")
    print(f"Total unrepairable failures due to lack of spares: {count_unrepairable_fails}")
    print(f"Total false failure alarms: {count_false_alarms}")


# -------- Spare Parts Management Functions -----------------------------

def queueRepair(sensedSystem, number_of_spares):
    """ Queue repairs for failed systems """

    # determine if the system is actually failed or if it's a false alarm
    system = sensedSystem.system

    if system.state == 0:  # system is actually failed

        # determine the component(s) that need repair and grab their MTTRs
        comps_to_repair = [comp for comp in system.comps if comp.state == 0]
        avg_repair_times = np.array([comp.MTTR for comp in comps_to_repair])

        # generate repair duration for each component
        act_repair_times = np.zeros(len(comps_to_repair))
        for i, comp in enumerate(comps_to_repair):

            # if non-repairable component, set repair time to infinity
            if avg_repair_times[i] == 'NR':
                print(f"Component '{comp.name}' is non-repairable.")

                # remove this component from the list to repair
                comps_to_repair.remove(comp)
                act_repair_times = np.delete(act_repair_times, i)
                continue

            # generate repair duration using a log-normal distribution
            repair_duration = np.floor(np.random.lognormal(mean=np.log(avg_repair_times[i]), sigma=0.5))
            # ensure the repair time is at least 1hr and at most 3*avg_repair_time (hrs)
            repair_duration= np.maximum(1, np.minimum(repair_duration, 3 * avg_repair_times[i]))

            # store the actual repair time
            act_repair_times[i] = repair_duration

        if number_of_spares <= len(comps_to_repair): 
            # need to handle insufficient spares case here (e.g., order and wait for new spares, or priority logic, etc.)                    
            # for simplicity, we will just skip the repair in this case
            print("Not enough spare parts available for repair!")
        
      
        elif len(comps_to_repair) == 0:
          # all failed components are non-repairable
            print(f"All failed components in system '{system.name}' are non-repairable.")

        else: 
            # use spare parts to repair the components
            number_of_spares -= len(comps_to_repair)  # decrement the number of spares available
            print(f"Repairing {len(comps_to_repair)} component(s) in system '{system.name}'.")

            # simulate repair time for each component
            for i, comp in enumerate(comps_to_repair):
                comp.history = np.concatenate([comp.history, np.full(int(act_repair_times[i]), -1)])  # update history to reflect repair time
                comp.state = 1  # set component state to operational
                comp.history[-1] = 1  # update history to reflect finished repair

        # no false alarm and repairs were handled accordingly
        return 0, sensedSystem, len(comps_to_repair)  # return 0 indicating a real failure repair
        
    # false alarm, no action needed
    elif system.state != 0:  # system is not actually failed
        print(f"False alarm for system '{system.name}'. No repair needed.")
        return 1, sensedSystem, 0

        



def orderMoreSpares(self, number_of_spares: int):
    """ Order more spare parts when inventory reaches a certain threshold """

    # Order more spare parts logic goes here later*** 
    pass