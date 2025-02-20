# import shipClass.MarkovChain as MarkovChain
import numpy as np
import networkx as nx

from matplotlib import pyplot as plt
from scipy.stats import weibull_min 

class MarkovChain:
    def __init__(self, states , transition_matrix)-> None:
        
        self.states = states
        self.transitionMatrix = transition_matrix
        self.history = []
        
        # set the initial state of the chain to "state 0: working"
        initial_state = states[0]
        self.history.append(initial_state)


    
# ---------------------- Useful Methods  ----------------------       

    def draw(self):
        """ Draw the Markov Chain as a directed graph """
        
        G = nx.DiGraph() # Directed graph G

        # Add edges to G based on transition matrix
        for i in range(len(self.states)):
            for j in range(len(self.states)):
                G.add_edge(self.states[i], self.states[j], weight=self.transitionMatrix[i][j])

        # Define positions for states (arranged in a straight line)
        pos = {self.states[i]: (i, 0) for i in range(len(self.states))}

        # Draw the graph with the defined positions
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue')

        # Draw edge labels with transition weights
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        
        # Show the plot
        plt.show()



# ---------------------- Monte Carlo Simulation  ----------------------       
        
    def simulate(self, num_steps):
        """ Simulate the Markov Chain over n steps """
        
        # Simulate the Markov Chain
        for i in range(num_steps):
            states = list(self.states.keys())
            state_names = list(self.states.values())
            
            currentState = self.currentState()  # name of the current state
            currentState_idx = list(self.states.values()).index(currentState)
                       
            next_state_idx = np.random.choice(states, p=self.transitionMatrix[currentState_idx])
            next_state = state_names[next_state_idx]        
            self.history.append(next_state)
            
            # if the current state is the first ocurance of a failure, store the time
            if next_state == state_names[-1] and self.history[-2] != state_names[-1]:
                self.failure_time = i
 

class Component(MarkovChain):

    def __init__(self, name: str, MTTF: float,  states: dict[int: str], transition_matrix )-> None:      # name:str, MTTF:float , shape:int = 2, scale: int = 10 
        """ Initialize the Component with the states and transition matrix """
        self.name = name

        # # failure distribution parameters
        self.MTTF = MTTF
        self.defineTransitionMatrix(MTTF)  # define the transition matrix based on the failure rate

        # self.shape = shape  # Shape parameter (beta)
        # self.scale = scale  # Scale parameter (eta)

        super().__init__(states, transition_matrix) # inheriting from MarkovChain class

# ---------------------- Reliability Modelling  ----------------------    
    def defineTransitionMatrix(self, 
                               MTTF:float = 1000.,
                               delta_t:float = 1.)-> np.array:
        """ Define the transition matrix based on the failure rate """

        # Desired Mean Time to Failure (MTTF)
        MTTF = self.MTTF  # in hours

        # Compute failure rate lambda
        failure_rate = 1 / MTTF  # λ = 1/MTTF

        # Compute transition probability
        p_failure = failure_rate * delta_t  # Probability of failure per time step

        # Define the transition matrix
        P = np.array([[1 - p_failure, p_failure], 
                    [0, 1]])

        # Print transition matrix
        print("Transition Matrix P:")
        print(P)

        return P
   

    
    
    def generateFailureTimes(self, simulation_period : int , plots = False) -> None:
        '''Generate random failure times from the failure distribution'''
        # Define the parameters
        beta = 1 # beta = shape
        eta =  20 # eta = scale

        # Generate random failure times
        failure_times = weibull_min.rvs(c=beta, scale=eta, size=1000)
        self.failure_times = failure_times
        
        if plots:
            # Plot the failure times
            plt.figure(figsize=(5, 5))
            plt.plot(failure_times)        
      
    def determineReliabilityCurve(self, plots = False):
        """ Determine the reliability curve of the component from failure times """
        
        failure_times = self.failure_times.sort() # sort the failure times in ascending order

        # solve for reliability curve over time
        rel_curve = []
        initial_reliability = len(failure_times) 
        for time in failure_times:
            rel_curve.append(initial_reliability) 
            initial_reliability -= 1
        rel_curve = np.array(rel_curve) / len(failure_times)  # normalize the reliability curve
        self.reliability_curve = rel_curve   
        
        if plots:
            # Plot the reliability curve
            plt.figure(figsize=(5, 5))
            plt.plot(failure_times, self.reliability_curve)

    def determineFailureRate(self, plots = False):
        """ Determine the failure rate of the component """
        failure_rate = []
        for i in range(len(self.reliability_curve) - 1):
            failure_rate.append(self.reliability_curve[i] - self.reliability_curve[i + 1])
        self.failure_rate = np.array(failure_rate)
        
        if plots:
            # Plot the failure rate
            plt.figure(figsize=(5, 5))
            plt.plot(self.failure_times, self.failure_rate)

        '''
        def startComp(self):
        # determine reliability curve and plot
        self.generateFailureTimes(simulation_period, plots = True)
        self.determineReliabilityCurve( plots = True)
        self.determineFailureRate( plots = True )
        '''

# ---------------------- Markov Random Proccess Modelling ----------------------       
        
    def defineTransitionMatrix(self, MTTF:float = 100.):
        
        """ Use the reliability distribution parameters to setup a transition matrix"""
               
        # default transition matrix
        transition_matrix = np.zeros((2, 2))
        transition_matrix[0, 0] = 1 - 1/MTTF
        transition_matrix[0, 1] = 1/MTTF
        transition_matrix[1, 0] = 0
        transition_matrix[1, 1] = 1
        
        print(transition_matrix)
        
        return transition_matrix

        








# # ---------------------- Testing ----------------------
""" # example  Component
    comp = Component('Comp1')

    # create a sub figure for 3 plots in one figure
    plt.figure(figsize=(10, 5))

    # generate failure times and plot
    plt.subplot(1, 3, 1)
    comp.generateFailureTimes()
    plt.hist(comp.failure_times, bins=10, density=True)

    # determine reliability curve and plot
    plt.subplot(1, 3, 2)
    comp.determineReliabilityCurve()
    times = comp.failure_times
    plt.plot(comp.failure_times, comp.reliability_curve[0:-1])

    # determine failure rate and plot
    plt.subplot(1, 3, 3)
    comp.determineFailureRate()
    plt.plot(comp.failure_times, comp.failure_rate)

    # show the plots
    plt.show()
    """