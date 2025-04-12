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
        working_state = list(sc.comp.states.keys())[-1]
        if sc.state != working_state: 
            # If the component is not in a working state, perform maintenance
            sc.reset()

    # Update the system state after maintenance
    system.state = system.SolveStructureFunction()

    return "Preventative maintenance performed successfully."
    
    
    
def correctiveMaintenance(system):
    """
    Perform corrective maintenance on a system.
    """
    for comp in system.comps:
        working_state = list(comp.comp.states.keys())[-1]  # get the working state of the component
        if comp.state != working_state:
            # If the component is not in a working state, perform maintenance

            comp.reset()

    # Update the system state after maintenance
    system.state = system.SolveStructureFunction()

    return "Corrective maintenance performed successfully."
    