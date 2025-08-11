from shipClass.MarkovChain import MarkovChain
import numpy as np


class Component(MarkovChain):
    i = 0   # class variable to keep track of component instances

    def __init__(self, 
                 name: str=f"Component_{i}", 
                 MTTF:float=50,
                 MTTR = 'NR',
                 states: dict[int: str] = {0 : 'failed', 1: 'working'})-> None:      
                # comp_transition_matrix: list[list[float]]=[[1.0, 0.0], 
                #                                            [0.02, 0.98]]
                
        """ Initialize the component as a Markov Chain object """
        
        # inheriting from MarkovChain class 
        # (super() holds self.state, self.history, and simulate(), plotHistory() and other methods)
        self.MTTF = MTTF
        self.MTTR = MTTR    # can be a float or a string (NR = non-repairable)
        self.states = states
        self.name = name 

        # increment the class variable i to keep track of component instances
        Component.i += 1

# ---------------------- Reliability Modelling ----------------------           

    def defineTwoStateTransitionMatrix(self, unmanned: bool = False):
        
        # grab the failure and repair rates
        fail_rate = 1/self.MTTF

        # check 1: is the vessel unmanned?
        if unmanned: 
            repair_rate = 0  # i.e. failure  is an absorbing state, 
                             # maintenance can only be done during port or when people board the ship or in dock
        
        # check 2: can the component be repaired? 
        elif type(self.MTTR) is str: 
            repair_rate = 0  # i.e. failure is an absorbing state 
                             # component cannot be repaired, it must be completly replaced since it is non-repairable

        else:
            repair_rate = 1/ self.MTTR  # component is repairable and will repair (assumes people are onboard)

        # set up transition matrix up and return it
        transition_matrix = np.array([[1-repair_rate, repair_rate], [fail_rate, 1-fail_rate]])
        return transition_matrix
        

    def initialize(self, unmanned:bool = False):
            self.transition_matrix = self.defineTwoStateTransitionMatrix(unmanned) # (all repair rates = 0 if unmanned = True)
            super().__init__(self.states, self.transition_matrix) 




# ----------------------------------- Useful Functions ------------------

    def grabFailureTime(self):
        """ from the component history, determine when the component failed,
            return None if not failed"""
        
        failure_state = list(self.states.keys())[0]

        try: 
            failure_time= self.history.index(failure_state)
        except ValueError:
            print(f"Component {self.name} has not failed yet.")
            failure_time="not failed"
        
        return failure_time
    







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