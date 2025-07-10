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
        Creates an (n x n)-state Markov chain transition matrix that meets a specified MTTF.
        The states are assumed to be 'Failed' (state 0), 'Operational_{n-1}, ..., 'Operational_1', 
        and 'Operational_0'. 
        
        ** This function assumes The Failed state is an absorbing state and transitions are only from
        an Operational state to the Failed state. All Operational states are assumed to have the same 
        probability of transitioning to the Failed state per time step to achieve the desired MTTF.

        Args:
        mttf: The desired Mean Time To Failure in the same time units as time_steps
        step_size: The duration of each time step in the Markov chain simulation.
        num_operational_states: The number of operational states (n). The total
                                number of states will be n+1 (n operational + 1 failed).

        Returns:
        An (n x n) numpy array representing the transition matrix.
        Returns None if a valid transition matrix cannot be created (e.g., mttf <= time_step).
        
        """

        # grab necessary parameters
        MTTF = self.MTTF
        n_states = len(self.states)
        num_operational_states = n_states - 1  # Assuming the last state is 'Failed'
        
        # initialize the transition matrix as (n x n) zeros
        transition_matrix = np.zeros((n_states, n_states))

        '''
        The Mean Time To Failure (MTTF) is the expected time to reach the Failed state
        from the Operational state. For this simple Markov chain, the MTTF is given by
            MTTF = time_step / (1-p)     
        We can solve for p: 
            p = 1 - (time_step / MTTF)
        '''
        # prob of transition to failed state 
        p_w = 1 - (step_size/MTTF)

        # prob of staying working 
        p_f = 1- p_w
        
        # add the probabilities to the transition matrix
        for i in range(num_operational_states):
            transition_matrix[n_states-1-i, n_states-1-i] =p_w     # stay in the same operational state
            transition_matrix[n_states-1-i, 0] =p_f # transition to the Failed state

        # make the Failed state an absorbing state
        transition_matrix[0, 0] = 1.0

        return transition_matrix


    def grabFailureTime(self):
        """ from the component history, determine when the component failed,
            return None if not failed"""
        
        failure_state = list(self.states.keys())[0]

        try: 
            failure_time= self.history.index(failure_state)
        except ValueError:
            failure_time= None
        
        return failure_time