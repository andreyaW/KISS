import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


class MarkovChain:
    def __init__(self, states , transition_matrix)-> None:
        
        ''' Initialize the Markov Chain with the given states and transition matrix 
        
            Args:
                states (dict): a dictionary of states (keys = state #, vals = state description)
                transition_matrix ( np.array): a matrix of transition probabilities between states
        '''
        # necessary attributes
        self.states = states
        self.transitionMatrix = transition_matrix
        self.history = []
        
        # setting initial state
        self.state = list(self.states.values())[-1]               
        print('Initial state:', self.state)
        self.history.append(self.state)


# ---------------------- Useful Methods  ----------------------       
    def currentState(self):
        """ Return the current state of the Markov Chain """
        return self.history[-1]

    def drawChain(self):
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

    def plotHistory(self):
        """ Plot the history of the Markov Chain """
        
        # Create a figure and axis
        fig, ax = plt.subplots()
        
        # Plot the history
        ax.plot(self.history, marker='o')
        
        # Set the title and labels
        ax.set_title('Markov Chain History')
        ax.set_xlabel('Time Step')
        ax.set_ylabel('State')
        
        # Show the plot
        plt.show()

# ---------------------- Monte Carlo Simulation  ----------------------       
        
    def simulate(self, number_of_steps: int) -> None:
        """ Simulate the Markov Chain over n steps """
        
        # Simulate the Markov Chain
        for i in range(number_of_steps):
            states = list(self.states.keys())
            state_names = list(self.states.values())
            
            currentState = self.currentState()  # name of the current state
            currentState_idx = list(self.states.values()).index(currentState)
                       
            next_state_idx = np.random.choice(states, p=self.transitionMatrix[currentState_idx])
            next_state = state_names[next_state_idx]        
            self.history.append(next_state)
            
            # if the current state is the first ocurance of a failure, store the time
            if next_state == state_names[-1] and self.history[-2] != state_names[-1]:
                self.failure_time = len(self.history)-1
                
                
                
   
# ---------------------- Example ---------------------- 

    # def get_failure_time(self):
    #     return self.failure_time