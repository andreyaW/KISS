# Maintenance.py
# This module contains functions for performing maintenance on a system.
# It includes both preventative and corrective maintenance functions.
from utils.helperFunctions import SolveStructureFunction

def periodicMaintenance(system, maintenance_delay):
    """
    Perform preventative maintenance on a system.
    
    Parameters:
    
    Returns:
    str: A message indicating the result of the maintenance.
    """


    for sc in system.comps:

        # If any component is not in a working state, perform maintenance on it
        working_state = list(sc.comp.states.keys())[-1]
        if sc.state != working_state: 
            # add maintenance delay to the component history
            maintenance_period = [-1] * maintenance_delay
            sc.comp.history += maintenance_period
            sc.sensedHistory += maintenance_period
            sc.extendedHistory += maintenance_period
            sc.extendedSensedHistory += maintenance_period

            # reset the component to its initial state
            sc.reset()

    # Update the system state after maintenance
    system.state = SolveStructureFunction(system.comps, system.parallels)
    print( "Periodic maintenance successfully performed.")

    return system


        
def correctiveMaintenance(system, maintenance_delay):
    """
    Perform corrective maintenance on a system.
    """
    # if the system is in a failed state
    if system.state == 0:  
        
        # Perform corrective maintenance on any components not in a useable state
        for comp in system.comps:
            failed_state = list(comp.comp.states.keys())[0]  # get the failed state of the component
            if comp.state == failed_state:
                # add maintenance delay to the component history
                maintenance_period = [-1] * maintenance_delay
                comp.history += maintenance_period
                comp.sensedHistory += maintenance_period
                comp.extendedHistory += maintenance_period
                comp.extendedSensedHistory += maintenance_period

                comp.reset()

    # Update the system state after maintenance
    system.state = system.SolveStructureFunction()

    return "Corrective maintenance performed successfully."
    