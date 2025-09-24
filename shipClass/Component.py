from shipClass.MarkovChain import MarkovChain
from shipClass.old_Model.Sensor2 import Sensor
from utils.excelFunctions import addTimeSteps, addTruth, finalFormatting

import numpy as np
import matplotlib.pyplot as plt
import xlsxwriter

class Component(MarkovChain):
    # i = 0   # class variable to keep track of component instances

    def __init__(self, 
                 name: str=f"Component", 
                 MTTF:float=50,
                 MTTR = 'NR',
                 states: dict[int: str] = {0 : 'major failure', 
                                           1: 'incipient failure/alert', 
                                           2: 'working'})-> None:      

        """ Three-state component model: 0=major failure, 1=incipient failure/alert, 2=working. Non-repairable by default

            Parameters
            ----------
            name: str
                The name of the component.
            MTTF: float
                Mean Time To Failure for the component.
            MTTR: float or str
                Mean Time To Repair for the component (can be non-repairable).
            states: dict[int: str]
                Mapping of state indices to state names.
        """
        self.MTTF = MTTF
        self.MTTR = MTTR    # can be a float or a string (NR = non-repairable)
        self.states = states
        self.name = name 

# ---------------------- Reliability Modelling ----------------------           
    def defineTwoStateTransitionMatrix(self, repairable: bool = False):
        
        # determine the failure rate of the component from the MTTF
        fail_rate = 1/self.MTTF

        # check: can the component be repaired / is vessel unmanned? 
        if repairable is False : 
            repair_rate = 0  # i.e. failure is an absorbing state 
                             # component cannot be repaired, it must be completly replaced since it is non-repairable
        else:
            repair_rate = 1/ self.MTTR  # component is repairable and will repair (assumes people are onboard)

        # set up transition matrix up and return it
        transition_matrix = np.array([[1-repair_rate, repair_rate], [fail_rate, 1-fail_rate]])
        return transition_matrix


    def defineThreeStateMatrix(self, repairable: bool = False):

        """ sets up a transition matrix for the component which considers it in one of three states, working, minor failure, or major failure"""
        #FAILURE/REPAIR MODEL:

        # determine the failure rate of the component from the MTTF
        lambda_ = 1/self.MTTF # failure rate

        # establish a minor and major failure rate schocastically
        lambda_d = lambda_ * np.random.rand()    # some probability that the fail is minor
        lambda_f = lambda_ - lambda_d            # some probability that the failure is major

        # check: can the component be repaired / is vessel unmanned? 
        if repairable is False:
            mu_ = 0  # i.e. unmanned, so even minor failures go unrepaired
        else: 
            #REPAIR MODEL 2:
            if self.MTTR == 'NR':
                mu_ = 0
            else:
                mu_ = 1/self.MTTR  # i.e. can conduct minor repair

        # add transition rates to the matrix
        transition_matrix = np.zeros((3,3))
        transition_matrix[0,0] = 1           # major failure is absorbing state
        transition_matrix[1,1] = 1-mu_       # stays in incipient failure
        transition_matrix[1,2] = mu_         # incipient failure to working (minor repair)
        transition_matrix[2,0] = lambda_f    # working to major failure
        transition_matrix[2,1] = lambda_d    # working to incipient failure
        transition_matrix[2,2] = 1- (lambda_d+lambda_f)   #stays working    

        return transition_matrix

    def initialize(self, repairable:bool = False):
            num_states = len(self.states)
            if num_states == 3:
                self.transition_matrix = self.defineThreeStateMatrix(repairable)
            else:
                self.transition_matrix = self.defineTwoStateTransitionMatrix(repairable) # (all repair rates = 0 if unmanned = True)
            
            # inheriting from MarkovChain class 
            super().__init__(self.states, self.transition_matrix) 

    def reset(self):
        """Resets the component to its initial state."""
        self.state = self.history[0]
        self.history = [self.state]

# ----------------------------------- Useful Functions ------------------
    def grabFailureTime(self):
        """ from the component history, determine when the component transitions from a working state"""
        working_state = list(self.states.keys())[-1]
        for i,state in enumerate(self.history):
            if state < working_state:
                return i
        return None
    
    
    def printHistory2Excel(self, filename: str, worksheet: str = None):
        """ print the history of the component to an excel sheet """
       
        with xlsxwriter.Workbook(filename) as workbook:
            if worksheet is None:
                if len(self.name) > 31:
                    sheet_name = self.name[:31]
                else: 
                    sheet_name = self.name
                worksheet = workbook.add_worksheet(sheet_name)

            num_data = len(self.history)
            for i in range(num_data):
                # add the time steps to the first column
                addTimeSteps(workbook, worksheet, i)

                # add truth states of the system and each sensed component to the row
                truth_data = [self.history[i]]
                if i == 0:
                    comp_truth_headers = ['Comp Truth State']
                    addTruth(workbook, worksheet, i, truth_data, comp_truth_headers)
                else:
                    addTruth(workbook, worksheet, i, truth_data)

            finalFormatting(worksheet, 1)