# Maintenance.py
# This file contains functions used for conducting maintenance on a system.
# It includes both preventative and corrective maintenance functions.

import scipy as sp

def determineMaintenancePeriod(mean=10, std_dev=5/6.28):
    ''' Determine the maintenance period for the system. '''
    
    # Generate a random maintenance period based on a normal distribution of times
    maintenance_time_dist = sp.stats.norm(loc=mean, scale=std_dev)
    maintenance_period = maintenance_time_dist.rvs(size=1)[0]

    # Ensure the maintenance period is a positive integer greater than or equal to 1
    maintenance_period = max(1, int(round(maintenance_period)))
            
    return maintenance_period


def maintenance(system, MTTR=10, TTR_var=5/6.28):
    """ Perform maintenance on the system. """

    maintenance_period = determineMaintenancePeriod(MTTR, TTR_var)

    # determine which comps need to be fixed
    for comp in system.comps:
        if comp.comp.state == 0:
            
            # making the components being repaired reflect repair time
            repair_time = [-1 for i in range(maintenance_period-1)]
            comp.comp.history += repair_time
            comp.sensedHistory+= repair_time

            #repair attached sensors as well
            for sensor in comp.sensors:
                sensor.history += repair_time   #sensor health
                sensor.readings += repair_time  #readings from component

            # reset the sensed comp to working state after PM
            comp.reset()

            # add the repair history to system history
            if len(system.history) < len(comp.comp.history):
                system.history += comp.comp.history[len(system.history):-2]
                system.sensedHistory += comp.sensedHistory[len(system.sensedHistory):-2]

        # leave the component not being repaired in thier current state until PM is done
        else:
            idle_time = [comp.comp.state for i in range(maintenance_period)]
            comp.comp.history+= idle_time
            comp.sensedHistory+= idle_time    

            # leave sensors in their current state
            for sensor in comp.sensors:
                idle_time = [sensor.state for i in range(maintenance_period)]
                sensor.history += idle_time
                idle_readings = [sensor.readings[-1] for i in range(maintenance_period)]
                sensor.readings += idle_readings        

    # update the system history to reflect the PM period
    system.reset()
    return maintenance_period


def correctiveMaintenance(system, time_step, MTTR=10):
    """ Perform corrective maintenance on the system. """
    CM_period = maintenance(system)
    return time_step + CM_period


def periodicMaintenance(system, time_step, PM_interval):
    """ Perform preventative maintenance on the system. """
    if time_step % PM_interval == 0:
        PM_period = maintenance(system)
        return time_step + PM_period
    return time_step

