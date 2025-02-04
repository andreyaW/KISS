import MarkovChain as mc
import scipy.stats as stats
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

    def __init__(self, name:str, shape:int = 2, scale: int = 10)-> None:
        self.name = name

        # failure distribution parameters
        self.shape = shape  # Shape parameter (beta)
        self.scale = scale  # Scale parameter (eta)


# ---------------------- Reliability Modelling  ----------------------    
    def generateFailureTimes(self):
        '''Generate random failure times from the failure distribution'''
        
        # temporary fixed failure distribution 
        shape = self.shape
        scale = self.scale
        self.failure_times = stats.weibull_min(c=shape, scale=scale).rvs(size=5000) 

    def determineReliabilityCurve(self):
       
        # Determine the reliability curve of the component
        shape = self.shape
        scale = self.scale
        failure_times = self.failure_times
        
        failure_times.sort()   # sort the failure times in ascending order
        initial_reliability = len(failure_times)  # initial reliability is the number of failure times
        reliability_curve = [1]  # empty list to store the reliability curve
        for time in failure_times:
            initial_reliability -= 1
            reliability_curve.append(initial_reliability / len(failure_times))
        self.reliability_curve = reliability_curve # store the reliability curve
  
    def determineFailureRate(self):
        # Determine the failure rate of the component
        shape = self.shape
        scale = self.scale
        failure_times = self.failure_times
        reliability_curve = self.reliability_curve
        self.failure_rate = stats.weibull_min(c=shape, scale=scale).pdf(failure_times) / reliability_curve[0:-1]

    def plotDistros(self):

        self.generateFailureTimes()
        self.determineReliabilityCurve()
        self.determineFailureRate()

        # Plot the failure distribution
        plt.figure(figsize=(15, 5))
        plt.subplot(1, 3, 1)
        plt.hist(self.failure_times, bins=10, density=True)
        plt.title('Failure Distribution')
        plt.xlabel('Failure Time')
        plt.ylabel('Density')
        
        # Plot the reliability curve
        plt.subplot(1, 3, 2)
        plt.plot(self.failure_times, self.reliability_curve[0:-1])
        plt.title('Reliability Curve')
        plt.xlabel('Failure Time')
        plt.ylabel('Reliability')

        # Plot the failure rate
        plt.subplot(1, 3, 3)
        plt.plot(self.failure_times, self.failure_rate)
        plt.title('Failure Rate')
        plt.xlabel('Failure Time')
        plt.ylabel('Failure Rate')

        plt.show()


# ---------------------- Markov Random Proccess Modelling ----------------------
    
            
        
    def defineTransitionMatrix(self, MTTF:float = 100., number_of_states: int = 2):
        
        """ Use the reliability distribution parameters to setup a transition matrix"""
        
        transition_matrix = np.zeros((number_of_states, number_of_states))
        for i in range(number_of_states):
            for j in range(number_of_states):
                if i == j:
                    transition_matrix[i, j] = 1 - 1/MTTF
                else:
                    transition_matrix[i, j] = 1/MTTF
        # print(transition_matrix)
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
              
    def simulate(self, steps):      
        """ simulating the component as a Markov Random Process over n steps"""
        self.setupMarkovChain()
        self.mC_model.simulate(steps)
        return self.mC_model.history
        
    def currentState(self):        
        """ return the current state of the component"""
        return self.mC_model.currentState()


        
        
