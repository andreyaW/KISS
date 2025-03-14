from shipClass.Component import Component
from shipClass.Sensor import Sensor
from shipClass.SensedComp import SensedComp

import numpy as np

class Maintainer(SensedComp):

    def __init__(self):
        """ Initialize the maintainer """
        self.cost = 0
        self.average_maintenance_cost = 0
        self.average_maintenance_delay = 10
        self.preventive_maintenance_interval = 25
        
    def diagnose(self, sensedComp) -> None:
        """ Diagnose the component """
        
        # get the sensed state of the component
        state = sensedComp.sensedState

        # if the component is working then no need to do maintenance
        if state == 'Working':
            pass
       
        # if state is 'Broken' then repair the component
        if state == 'Broken':
            repairedSensedComp = self.corrective_maintaince(sensedComp)
            sensedComp = repairedSensedComp

        return sensedComp

    def corrective_maintaince(self, sensedComp) -> None:
        """ Maintain the component (Good as New Repair)"""
    
        # repair the component and its sensors (Reinitialize the Markov Chain models)
        comp_name = sensedComp.comp.name
        comp_states = sensedComp.comp.states
        comp_transition_matrix = sensedComp.comp.transitionMatrix   
        comp = Component(comp_name, comp_states, comp_transition_matrix)
        
        sensors_name = sensedComp.sensors.name
        sensors_states = sensedComp.sensors.states
        sensors_transition_matrix = sensedComp.sensors.transitionMatrix
        sensors = Sensor(sensors_name, sensors_states, sensors_transition_matrix)

        # updating to a working sensed component
        sensedComp_R= SensedComp(comp, sensors)

        # keep previous history of operation and add maintenance delay
        maintenance_delay = [sensedComp.state for i in range(self.average_maintenance_delay)]   # comp stays in its state until repair is complete
        sensedComp_R.history = sensedComp.history + maintenance_delay
        sensedComp_R.sensedHistory = sensedComp.sensedHistory + maintenance_delay 
        
        # add to maintainer cost
        self.cost += 1
        return sensedComp_R



    def preventive_maintaince(self, sensedComp) -> None:
        """ Maintain the component regularly (Preventive Maintenance)"""
        
        flag = np.mod(len(sensedComp.history), self.preventive_maintenance_interval) == 0
        
        if flag:
            sensedComp = self.corrective_maintaince(sensedComp)

        return sensedComp