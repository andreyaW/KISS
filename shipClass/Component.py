from shipClass.MarkovChain import MarkovChain

import numpy as np

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
        # determine the failure rate of the component from the MTTF
        lambda_ = 1/self.MTTF # failure rate

        # establish a minor and major failure rate schocastically
        lambda_d = lambda_ * np.random.rand()    # some probability that the fail is minor
        lambda_f = lambda_ - lambda_d            # some probability that the failure is major

        # check: can the component be repaired / is vessel unmanned? 
        if repairable is False:
            mu_ = 0  # i.e. unmanned, so even minor failures go unrepaired

            # REPAIR MODEL 1:
            # mu_d = 0
            # mu_f = 0
        else: 
            #REPAIR MODEL 2: 
            mu_ = 1/self.MTTR  # i.e. can conduct minor repair

            #REPAIR MODEL 1:
            # mu_ = 1/self.MTTR    # component is repairable and will repair (assumes people are onboard)        
            # mu_d = mu_ * np.random.rand()  # some probability that the repair is minor
            # mu_f = mu_ - mu_d              # some probability that the repair is major


        #REPAIR MODEL 2:
        transition_matrix = np.zeros((3,3))
        transition_matrix[0,0] = 1           # major failure is absorbing state
        transition_matrix[1,1] = 1-mu_       # stays in incipient failure
        transition_matrix[1,2] = mu_         # incipient failure to working (minor repair)
        transition_matrix[2,0] = lambda_f    # working to major failure
        transition_matrix[2,1] = lambda_d    # working to incipient failure
        transition_matrix[2,2] = 1- (lambda_d+lambda_f)   #stays working    

        # REPAIR MODEL 1: 
        # # setup the transition matrix 
        # transition_matrix = np.zeros((3,3)) 
        # transition_matrix[0,0] = 1 - mu_f   # stays in major failure
        # transition_matrix[0,2] = mu_f       # major failure to working
        # transition_matrix[1,1] = 1 - mu_d   # stays in incipient failure
        # transition_matrix[1,2] = mu_d       # incipient failure to working
        # transition_matrix[2,0] = lambda_f   # working to major failure
        # transition_matrix[2,1] = lambda_d   # working to incipient failure
        # transition_matrix[2,2] = 1- (lambda_d+lambda_f)   #stays working

        return transition_matrix


    def initialize(self, repairable:bool = False):
            num_states = len(self.states)
            if num_states == 3:
                self.transition_matrix = self.defineThreeStateMatrix(repairable)
            else:
                self.transition_matrix = self.defineTwoStateTransitionMatrix(repairable) # (all repair rates = 0 if unmanned = True)
            
            # inheriting from MarkovChain class 
            super().__init__(self.states, self.transition_matrix) 


# ----------------------------------- Useful Functions ------------------

    # def grabFailureTime(self):
    #     """ from the component history, determine when the component failed,
    #         return None if not failed"""
        
    #     failure_state = list(self.states.keys())[0]

    #     try: 
    #         failure_time= self.history.index(failure_state)
    #     except ValueError:
    #         print(f"Component {self.name} has not failed yet.")
    #         failure_time="not failed"
        
    #     return failure_time
    
    def grabFailureTime(self):
        """ from the component history, determine when the component transitions from a working state"""
        working_state = list(self.states.keys())[-1]
        for i,state in enumerate(self.history):
            if state < working_state:
                return i
        return None

'''
    def createWeibullLikeTransitionMatrix(self, beta=2.0, step_size=1):
        """
        Create a Markov chain transition matrix that approximates a Weibull failure distribution.
        Uses a degradation chain with state-dependent transition probabilities.
        
        Parameters:
        - beta: Weibull shape parameter
        - step_size: time duration per step
        
        Returns:
        - transition_matrix: (n x n) numpy array
        """
        import numpy as np

        MTTF = self.MTTF
        n_states = len(self.states)  # assume state 0 is Failed, states 1..N are degradation levels
        num_degradation_steps = n_states - 1  # exclude absorbing failure state

        transition_matrix = np.zeros((n_states, n_states))

        # Make failed state absorbing
        transition_matrix[0, 0] = 1.0

        # Estimate average number of steps to failure = MTTF / step_size
        expected_steps = MTTF / step_size

        # Compute base_p so that the expected time to failure ≈ MTTF
        # Estimate normalization using harmonic-like sum of weights
        weights = [(i ** (beta - 1)) for i in range(1, n_states)]
        total_weight = sum(weights)
        base_p = num_degradation_steps / (expected_steps * total_weight)

        # Build transitions from state i to i-1 (toward failure)
        for i in range(1, n_states):
            weight = i ** (beta - 1)
            p = base_p * weight
            p = min(p, 1.0)
            transition_matrix[i, i - 1] = p       # degrade
            transition_matrix[i, i] = 1.0 - p     # stay

        return transition_matrix
'''