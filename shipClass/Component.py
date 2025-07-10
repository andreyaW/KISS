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

        transition_matrix = self.createMTTFtransitionMatrix()
        super().__init__(states, transition_matrix)  

        # declare component attributes
        self.name = name

# ---------------------- Reliability Modelling ----------------------       
    def createMTTFtransitionMatrix(self, step_size=1):
        """
        Create a Markov transition matrix such that the overall MTTF is achieved.
        This version creates a linear degradation chain leading to failure.
        """

        MTTF = self.MTTF
        n_states = len(self.states)
        num_operational_states = n_states - 1  # Exclude the Failed state (assumed to be state 0)

        transition_matrix = np.zeros((n_states, n_states))

        # Make the Failed state (state 0) absorbing
        transition_matrix[0, 0] = 1.0

        # The expected number of steps to reach the Failed state is MTTF.
        # So average time in each operational state = MTTF / num_operational_states
        p = step_size / (MTTF / num_operational_states)  # transition prob to next state

        for i in range(1, n_states):
            if i == 1:
                # transition from state 1 to failed (state 0)
                transition_matrix[i, 0] = p
                transition_matrix[i, i] = 1 - p
            else:
                # transition from state i to i-1 (degradation)
                transition_matrix[i, i - 1] = p
                transition_matrix[i, i] = 1 - p

        return transition_matrix



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