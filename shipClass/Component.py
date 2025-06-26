from shipClass.MarkovChain import MarkovChain
import numpy as np

class Component(MarkovChain):

    def __init__(self, 
                 name: str, 
                 states: dict[int: str], 
                 MTTF )-> None:      
        
        """ Initialize the component as a Markov Chain object """
        
        # inheriting from MarkovChain class 
        # (super() holds self.state, self.history, and simulate(), plotHistory() and other methods)
        self.MTTF = MTTF
        self.states = states
        self.name = name

        transition_matrix = self.create_mttf_markov_chain_n_states()
        super().__init__(states, transition_matrix)  

        # declare component attributes
        self.name = name

# ---------------------- Reliability Modelling ----------------------       

    def create_mttf_markov_chain_n_states(self, time_step=1):
        """
        Creates an (n+1)-state Markov chain transition matrix that meets a specified MTTF.

        The states are assumed to be 'Operational_0', 'Operational_1', ...,
        'Operational_{n-1}' and 'Failed' (state n).
        ** Assumes transitions are only from an Operational state to the Failed state.
        All Operational states are assumed to have the same probability of transitioning
        to the Failed state per time step to achieve the desired MTTF.
        The Failed state is an absorbing state.

        The Mean Time To Failure (MTTF) from any Operational state is the expected
        time to reach the Failed state.
        MTTF = time_step / P(transition to Failed from any operational state)
        
        # The probability of staying in the operational state cluster (or transitioning
        # between operational states) is 1 - prob_to_failed for each operational state.
        # For this simplified model, we assume all remaining probability is for staying
        # within the operational states (e.g., equally distributed among other operational
        # states including the current one, or just staying in the current one if no
        # transitions between operational states are modeled explicitly).
        # We'll assume for this simple model that the remaining probability is distributed
        # among the *other* operational states and potentially staying in the current one.
        # A simple way to distribute this is equally among all operational states, including the current one.
        # Let's simplify further: assume the remaining probability (1 - prob_to_failed)
        # is distributed among the 'num_operational_states' operational states.
        # A common pattern is to assume the system stays in the same operational state
        # with probability (1 - prob_to_failed) and transitions to failed with prob_to_failed.
        # Or, if states represent progressive degradation, the probability might be
        # of moving to the *next* operational state.
        # Let's implement the simple case: from any operational state, you either stay
        # in that state or transition to failed. This implies no transitions *between*
        # operational states. This still gives MTTF = time_step / prob_to_failed
        # from any operational state as long as state 0 is the starting state.

        # If states represent a sequence 0 -> 1 -> ... -> n-1 -> n (Failed),
        # then from state i (i < n-1), prob to i+1 is p, prob to n (Failed) is q.
        # From state n-1, prob to n (Failed) is r.
        # This makes the MTTF calculation more complex.


        Args:
        mttf: The desired Mean Time To Failure in the same time units as time_step.
        time_step: The duration of each step in the Markov chain.
        num_operational_states: The number of operational states (n). The total
                                number of states will be n+1 (n operational + 1 failed).

        Returns:
        An (n+1)x(n+1) numpy array representing the transition matrix.
        Returns None if a valid transition matrix cannot be created (e.g., mttf <= time_step).
        
        """
        # grab necessary parameters
        mttf = self.MTTF
        total_states = len(self.states)
        num_operational_states = total_states - 1  # Assuming the last state is 'Failed'
        
        # initialize the transition matrix as zeros
        transition_matrix = np.zeros((total_states, total_states))

        # determine relevant probabilities at this time step
        prob_to_failed = time_step / mttf

        if prob_to_failed > 1:
            prob_stay_operational = 1- prob_to_failed

            # normalize the values to ensure they are non-negative
            sum_prob = prob_to_failed + prob_stay_operational
            prob_to_failed /= sum_prob

        prob_stay_operational = 1 - prob_to_failed
        
        # add the probabilities to the transition matrix
        for i in range(num_operational_states):
            transition_matrix[i, i] = prob_stay_operational     # stay in the same operational state
            transition_matrix[i, num_operational_states] = prob_to_failed # transition to the Failed state

        # make the Failed state an absorbing state
        transition_matrix[num_operational_states, num_operational_states] = 1.0

        # # print the transition matrix for debugging
        print(f"Transition matrix for {self.name} at time step {time_step}:\n{transition_matrix}")
        return transition_matrix


    def simulate(self, time_step: int):
        """
        Simulates the component's Markov chain for a given time step.
        Args:
        time_step: The current time step for the simulation.
        """
        # Update the transition matrix based on the current time step
        self.transitionMatrix = self.create_mttf_markov_chain_n_states(time_step)
        super().simulate()



    '''
    #   if mttf <= time_step:
    #     print("Error: MTTF must be greater than the time step.")
    #     return None

        if num_operational_states <= 0:
            print("Error: Number of operational states must be positive.")
        return None

        total_states = num_operational_states + 1 # Operational states + Failed state

        # Calculate the probability of transitioning to the Failed state from any
        # operational state. This probability is assumed to be the same for all
        # operational states for this simplified model to meet the single MTTF requirement.
        prob_to_failed = time_step / mttf

    #   if prob_to_failed > 1:
    #        print(f"Error: Calculated probability to failed ({prob_to_failed:.4f}) is greater than 1. "
    #              "Increase MTTF or decrease time_step.")
    #        return None

        # NEXT: If we want to model a more complex scenario where operational states
        # represent a sequence of degradation (e.g., 0 -> 1 -> ... -> n-1), we would
            # If states represent a sequence 0 -> 1 -> ... -> n-1 -> n (Failed),
            # then from state i (i < n-1), prob to i+1 is p, prob to n (Failed) is q.
            # From state n-1, prob to n (Failed) is r.
            # This makes the MTTF calculation more complex.

            # Let's stick to the interpretation closest to the original 2-state model:
            # there's a set of operational states, and from *any* operational state, there's
            # a probability 'q' of going to the single 'Failed' state, and probability '1-q'
            # of staying within the set of operational states (e.g., staying in the same state).
            # The MTTF from any operational state is time_step / q. So, q = time_step / mttf.

        # Initialize the transition matrix with zeros
        transition_matrix = np.zeros((total_states, total_states))

        # Fill in transitions from operational states (0 to num_operational_states-1)
        prob_stay_operational = 1 - prob_to_failed

    for i in range(num_operational_states):
        # Assume the probability of staying in the *set* of operational states
        # is distributed among the operational states.
        # For simplicity, let's assume the probability of staying in the *same*
        # operational state is `prob_stay_operational`.
        transition_matrix[i, i] = prob_stay_operational
        # And the probability of transitioning to the Failed state is `prob_to_failed`.
        transition_matrix[i, num_operational_states] = prob_to_failed

    # The Failed state (index num_operational_states) is an absorbing state
    transition_matrix[num_operational_states, num_operational_states] = 1.0

    # Optional: If transitions between operational states are needed,
    # the prob_stay_operational would be distributed differently.
    # E.g., probability of moving to the next state (i+1) could be prob_stay_operational,
    # and the diagonal would be 0 for operational states except the last one.
    # This simplified model assumes no transitions between operational states explicitly.

    return transition_matrix
    '''