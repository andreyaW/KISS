from shipClass.MarkovChain import MarkovChain
import numpy as np

class Component(MarkovChain):

    def __init__(self, 
                 name: str, 
                 states: dict[int: str], 
                 MTTF=50 )-> None:      
        
        """ Initialize the component as a Markov Chain object """
        
        # inheriting from MarkovChain class 
        # (super() holds self.state, self.history, and simulate(), plotHistory() and other methods)
        self.MTTF = MTTF
        self.states = states
        self.name = name

        self.transition_matrix = self.createWeibullLikeTransitionMatrix()
        super().__init__(states, self.transition_matrix)  

        # declare component attributes
        self.name = name

# ---------------------- Reliability Modelling ----------------------       
    # def createMTTFtransitionMatrix(self, step_size=1):
    #     """
    #     Create a Markov transition matrix such that the overall MTTF is achieved.
    #     This version creates a linear degradation chain leading to failure.
    #     """

    #     MTTF = self.MTTF
    #     n_states = len(self.states)
    #     num_operational_states = n_states - 1  # Exclude the Failed state (assumed to be state 0)

    #     transition_matrix = np.zeros((n_states, n_states))

    #     # Make the Failed state (state 0) absorbing
    #     transition_matrix[0, 0] = 1.0

    #     # The expected number of steps to reach the Failed state is MTTF.
    #     # So average time in each operational state = MTTF / num_operational_states
    #     p = step_size / (MTTF / num_operational_states)  # transition prob to next state

    #     for i in range(1, n_states):
    #         if i == 1:
    #             # transition from state 1 to failed (state 0)
    #             transition_matrix[i, 0] = p
    #             transition_matrix[i, i] = 1 - p
    #         else:
    #             # transition from state i to i-1 (degradation)
    #             transition_matrix[i, i - 1] = p
    #             transition_matrix[i, i] = 1 - p

    #     return transition_matrix


    # def createWeibullLikeTransitionMatrix(self, beta=2.0, step_size=1):
    #     """
    #     Create a Markov chain transition matrix that approximates a Weibull failure distribution.
    #     Uses a degradation chain with state-dependent transition probabilities.
        
    #     Parameters:
    #     - beta: Weibull shape parameter
    #     - step_size: time duration per step
        
    #     Returns:
    #     - transition_matrix: (n x n) numpy array
    #     """
    #     import numpy as np

    #     MTTF = self.MTTF
    #     n_states = len(self.states)  # assume state 0 is Failed, states 1..N are degradation levels
    #     num_degradation_steps = n_states - 1  # exclude absorbing failure state

    #     transition_matrix = np.zeros((n_states, n_states))

    #     # Make failed state absorbing
    #     transition_matrix[0, 0] = 1.0

    #     # Estimate average number of steps to failure = MTTF / step_size
    #     expected_steps = MTTF / step_size

    #     # Compute base_p so that the expected time to failure ≈ MTTF
    #     # Estimate normalization using harmonic-like sum of weights
    #     weights = [(i ** (beta - 1)) for i in range(1, n_states)]
    #     total_weight = sum(weights)
    #     base_p = num_degradation_steps / (expected_steps * total_weight)

    #     # Build transitions from state i to i-1 (toward failure)
    #     for i in range(1, n_states):
    #         weight = i ** (beta - 1)
    #         p = base_p * weight
    #         p = min(p, 1.0)
    #         transition_matrix[i, i - 1] = p       # degrade
    #         transition_matrix[i, i] = 1.0 - p     # stay

    #     return transition_matrix


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