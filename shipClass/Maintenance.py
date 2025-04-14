# Maintenance.py
# This module contains functions for performing maintenance on a system.
# It includes both preventative and corrective maintenance functions.


def periodicMaintenance(system):
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
            sc.reset()

    # Update the system state after maintenance
    system.state = system.SolveStructureFunction()

    return "Preventative maintenance performed successfully."
    
    
    
def correctiveMaintenance(system):
    """
    Perform corrective maintenance on a system.
    """
    # if the system is in a failed state
    if system.state == 0:  
        
        # Perform corrective maintenance on any components not in a useable state
        for comp in system.comps:
            failed_state = list(comp.comp.states.keys())[0]  # get the failed state of the component
            if comp.state == failed_state:
                comp.reset()

    # Update the system state after maintenance
    system.state = system.SolveStructureFunction()

    return "Corrective maintenance performed successfully."
    