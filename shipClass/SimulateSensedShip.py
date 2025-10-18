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
def simulateWithSpareParts(sensedShip, number_of_spares: int, time_steps: int):
    """ Simulate the ship with spare parts logic """
    
    count_unrepairable_fails = 0  # counter for unrepairable failures(i.e. times with no spares left)

    for t in range(time_steps):

        sensedShip.simulate(1)  # simulate one time step

        # check for failed systems and replace with spares if available
        for sensedSystem in sensedShip.sensedSystems:
            if sensedSystem.sensedState == 0:  # if the system is sensed as failed
                if number_of_spares > 0:
                    queueRepair(sensedSystem.system)  # queue repair for the system
                    number_of_spares -= 1  # decrement the number of spares
                else:

                    # no spares available, order new part logic goes here later***
                    pass
            else:
                continue  # system is operational, do nothing



# -------- Spare Parts Management Functions -----------------------------
def queueRepair(sensedSystem):
    """ Queue repairs for failed systems """

    system = sensedSystem.system

    # determine which components need repair
    comp_states = np.array([comp.state for comp in system.comps])
    failed_indices = np.where(comp_states == 0)[0]  # indices of failed components

    num_failed = len(failed_indices)
    if num_failed == 1:
        comp_to_repair = system.comps[failed_indices[0]]
        avg_repair_time = comp_to_repair.MTTF

        time_until_repair = np.floor(np.random.lognormal(mean=np.log(avg_repair_time), sigma=0.5))

        # ensure the repair time is at least 1 and at most 3*avg_repair_time
        time_until_repair = max(1, min(time_until_repair, 3 * avg_repair_time))
        repair_time = time_until_repair

    elif num_failed > 1:
        # need to add priority repairs logic based on some criteria (e.g., criticality, repair time)
        # for simplicity, we will just repair the first failed component here
        pass 
    # need to add repair time logic here later***

    # return the system to operational state after repair time
    system.reset()  # replace with a spare (reset the system)

        



def orderMoreSpares(self, number_of_spares: int):
    """ Order more spare parts when inventory reaches a certain threshold """

    # Order more spare parts logic goes here later*** 
    pass