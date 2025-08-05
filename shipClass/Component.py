from shipClass.MarkovChain import MarkovChain
import numpy as np

class Component(MarkovChain):

    def __init__(self, 
                 name: str, 
                 states: dict[int: str] = {0 : 'failed', 1: 'working'}, 
                 MTTF:float=50,
                 MTTR = 'NR')-> None:      
                # comp_transition_matrix: list[list[float]]=[[1.0, 0.0], 
                #                                            [0.02, 0.98]]
                
        """ Initialize the component as a Markov Chain object """

        # inheriting from MarkovChain class 
        # (super() holds self.state, self.history, and simulate(), plotHistory() and other methods)
        self.MTTF = MTTF
        self.MTTR = MTTR    # can be a float or a string (NR = non-repairable)
        self.states = states
        self.name = name 

        

# ---------------------- Reliability Modelling ----------------------           

    # def initialize(self, unmanned:bool = False):
    #     self.transition_matrix = self.defineTwoStateTransitionMatrix(unmanned)
    #     super().__init__(self.states, self.transition_matrix) 


    # def defineTwoStateTransitionMatrix(self, unmanned: bool = False):
        
    #     # grab the failure and repair rates
    #     fail_rate = 1/self.MTTF

    #     if unmanned: 
    #         repair_rate = 0  # i.e. failure  is an absorbing state, maintenance can only be done during port or when ship is boarded
        
    #     elif type(self.MTTR) is str: 
    #         repair_rate = 0  # i.e. failure is an absorbing state and component must be replaced since it is non-repairable

    #     else:
    #         repair_rate = 1/ self.MTTR  # component is repairable and will repair (assumes people are onboard)

    #     # set the transition matrix up and store
    #     transition_matrix = np.array([[1-repair_rate, repair_rate], [fail_rate, 1-fail_rate]])
        
    #     return transition_matrix
        

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
 def createWeibullLikeTransitionMatrix(self, beta=1.0, step_size=1, tolerance=1e-2):
        """
        Create a degradation-based Markov transition matrix with Weibull-like hazard
        and calibrated to match the given MTTF.
        """

        MTTF = self.MTTF
        n_states = len(self.states)
        num_transient = n_states - 1  # All except failed state (state 0)

        # Precompute weights
        weights = np.array([i ** (beta - 1) for i in range(1, n_states)])

        def build_matrix(base_p):
            T = np.zeros((n_states, n_states))
            T[0, 0] = 1.0  # failed state absorbing
            for i in range(1, n_states):
                p = base_p * weights[i - 1]
                p = min(p, 1.0)
                T[i, i - 1] = p
                T[i, i] = 1 - p
            return T

        def expected_time_to_failure(T):
            Q = T[1:, 1:]  # exclude absorbing state
            I = np.eye(num_transient)
            N = np.linalg.inv(I - Q)  # fundamental matrix
            t = N @ np.ones((num_transient, 1))
            return t[-1, 0] * step_size  # assume starting from healthiest state

        # Binary search to calibrate base_p
        low, high = 1e-6, 1.0
        best_p = None
        for _ in range(100):
            mid = (low + high) / 2
            T = build_matrix(mid)
            etf = expected_time_to_failure(T)
            if abs(etf - MTTF) < tolerance:
                best_p = mid
                break
            elif etf > MTTF:
                low = mid
            else:
                high = mid

        if best_p is None:
            best_p = mid  # best guess

        return build_matrix(best_p)
'''


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