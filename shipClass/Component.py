import MarkovChain as mc
import scipy.stats as stats

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
    def setupMarkovChain(self, states:int, transition_matrix: list):

        # inheriting MarkovChain class for modelling the component
        self.mC_model = mc.MarkovChain()

        states = {0: 'Good', 1: 'Bad'}
        transition_matrix = [[0.9, 0.1], [0.2, 0.8]]

        self.mC_model.setupMarkovChain(states, transition_matrix)


    def simulate(self):
        self.mC_model.simulate(1000)
        self.mC_model.plotSimulation()