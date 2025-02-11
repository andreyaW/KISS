import shipClass.MarkovChain as mc
from scipy.stats import weibull_min 
import numpy as np

from matplotlib import pyplot as plt

class Component:
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

    def __init__(self, name:str, MTTF:float , shape:int = 2, scale: int = 10)-> None:
        self.name = name
        self.MTTF = MTTF

        # failure distribution parameters
        self.shape = shape  # Shape parameter (beta)
        self.scale = scale  # Scale parameter (eta)


# ---------------------- Reliability Modelling  ----------------------    
    def generateFailureTimes(self, simulation_period : int , plots = False):
        '''Generate random failure times from the failure distribution'''
        # Define the parameters
        beta = 5 # beta = shape
        eta =  92 # eta = scale

        # Generate random failure times
        failure_times = weibull_min.rvs(c=beta, scale=eta, size=1000)
        self.failure_times = failure_times
        # print(failure_times.mean())             # Calculate the mean
        
        if plots:
            # Plot the failure times
            plt.figure(figsize=(5, 5))
            plt.plot(failure_times)        
      
    def determineReliabilityCurve(self, plots = False):
        # Determine the reliability curve of the component from failure times
        failure_times = self.failure_times
        failure_times.sort()   # sort the failure times in ascending order

        initial_reliability = len(failure_times)  # initial reliability is the number of failure times
        rel_curve = []  # store the reliability curve
        for time in failure_times:
            rel_curve.append(initial_reliability) 
            initial_reliability -= 1

        rel_curve = np.array(rel_curve) / len(failure_times)  # normalize the reliability curve
        self.reliability_curve = rel_curve # store the reliability curve
        
        if plots:
            # Plot the reliability curve
            plt.figure(figsize=(5, 5))
            plt.plot(failure_times, self.reliability_curve)

    def determineFailureRate(self, plots = False):
        # Determine the failure rate of the component from the reliability curve
        failure_rate = []
        for i in range(len(self.reliability_curve) - 1):
            failure_rate.append(self.reliability_curve[i] - self.reliability_curve[i + 1])
        self.failure_rate = np.array(failure_rate)
        
        if plots:
            # Plot the failure rate
            plt.figure(figsize=(5, 5))
            plt.plot(self.failure_times, self.failure_rate)



# ---------------------- Markov Random Proccess Modelling ----------------------       
        
    def defineTransitionMatrix(self, MTTF:float = 100., number_of_states: int = 2):
        
        """ Use the reliability distribution parameters to setup a transition matrix"""
        
        transition_matrix = np.zeros((number_of_states, number_of_states))
        
        # calculate the probability of transitioning from working to broken
        p = 6 / MTTF 

        # setup the transition matrix
        transition_matrix[0, 0] = 1 - p
        transition_matrix[0, 1] = p


        return transition_matrix
    
    def setupMarkovChain(self, 
                        states:dict = {0: 'Working', 1: 'Broken'}, 
                        transition_matrix: list = None):

        """ Using the inherent Markov Chain class to model a component """
        # setup the transition matrix if one is not given
        if transition_matrix is None:
            transition_matrix = self.defineTransitionMatrix()

        # inheriting MarkovChain class from MarkovChain.py
        self.mC_model = mc.MarkovChain()
        self.mC_model.setupMarkovChain(states, transition_matrix)

# ---------------------- Monte Carlo Simulation  ----------------------       

    def simulate(self, simulation_period: int):      
        """ simulating the component as a Markov Random Process over n steps"""
        
        # for t in simulation_period:

        # determine reliability curve and plot
        self.generateFailureTimes(simulation_period, plots = True)
        self.determineReliabilityCurve( plots = True)
        self.determineFailureRate( plots = True ) 

            # # setup the Markov Chain
            # self.determineTransitionMatrix()
            # self.setupMarkovChain(states, transition_matrix)
            # self.mC_model.simulate(steps)
            # return self.mC_model.history
        
    def currentState(self):        
        """ return the current state of the component"""
        return self.mC_model.currentState()


        
        
