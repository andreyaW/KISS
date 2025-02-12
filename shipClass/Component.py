import shipClass.MarkovChain as MarkovChain
from scipy.stats import weibull_min 
import numpy as np

from matplotlib import pyplot as plt

class Component(MarkovChain):

    def __init__(self, name:str, MTTF:float , shape:int = 2, scale: int = 10)-> None:        
        self.name = name

        # failure distribution parameters
        self.MTTF = MTTF
        self.shape = shape  # Shape parameter (beta)
        self.scale = scale  # Scale parameter (eta)

        # setup the component as a Markov Chain
        states = {0: 'Working', 1: 'Broken'}
        transition_mat = self.defineTransitionMatrix(MTTF)
        super.__init__(states, transition_mat) # inheriting from MarkovChain class

# ---------------------- Reliability Modelling  ----------------------    
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