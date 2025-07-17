import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from utils.helperFunctions import get_key_by_value


class MarkovChain:
    def __init__(self, states: dict , transition_matrix : np.array )-> None:
        
        ''' Initialize the Markov Chain with the given states and transition matrix 
        
            Args:
                states (dict): a dictionary of states (keys = state #, vals = state description)
                transition_matrix ( np.array): a matrix of transition probabilities between states
        '''
        # necessary attributes
        self.states = states
        self.transitionMatrix = transition_matrix
        
        # setting initial state
        self.state = list(self.states.keys())[-1]               
        self.history = [self.state]                     # array to keep track of the history of states

# ---------------------- Useful Methods  ----------------------       
    
    def get_failure_time(self):
        """ Determine from the history when the object fails """
        failure_state = list(self.states.keys())[0]
        
        # find the first occurrence of the failure state in the history
        for i, state in enumerate(self.history):
            if state == failure_state:
                self.failure_time = i
                break       
        return self.failure_time


    def drawChain(self, name:str= None):
        """ Draw the Markov Chain as a directed graph """
        # create a figure for the drawing and give it a title if necessary
        plt.figure(figsize=(10,5))

        if name != None:
            ax = plt.gca()
            ax.set_title(name)

        # initialize a nx directed graph
        G = nx.DiGraph() 

        # Add edges to G based on transition matrix
        for i in range(len(self.states)):
            for j in range(len(self.states)):
                G.add_edge(self.states[i], self.states[j], weight=self.transitionMatrix[i][j])

        # Define positions for states (arranged in a straight line)
        pos = {self.states[i]: (i, 0) for i in range(len(self.states))}
        pos[self.states[0]] = (i+1, -1)  # Position the first state (failure) lower then others
        
        # Draw the graph with the defined positions
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', alpha=0.3,
                                          arrowsize=60, arrowstyle = '-', 
                                          font_size=10, font_weight='bold')

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
        y_ticks = list(self.states.keys())
        y_labels = [self.states[i] for i in y_ticks]
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)
        
        # Show the plot
        plt.show()

# ---------------------- Monte Carlo Simulation  ----------------------       

    def simulate(self, number_of_steps: int = 1) -> None:
        """ Simulate the Markov Chain over n steps """
        
        # Simulate the Markov Chain
        for i in range(number_of_steps):
            states = list(self.states.keys())   # get the keys of the all states (0, 1, 2, ...)      
            currentState_idx = self.state       # get the index of the current state
                       
            # randomly select and update the next state using probabilities from the transition matrix
            next_state = int(np.random.choice(states, p=self.transitionMatrix[currentState_idx]))       
            


                # code to catch self improving states
                # if next_state > currentState_idx:   # if the next state is higher than the current state, it means a failure has occurred
                #     print(f"There has been an error in simulation.")
                #     break
                    
            self.state = next_state
            self.history.append(next_state)     # append the new state to the history
       
    def reset(self):
        """ Reset the Markov Chain to its initial state and delete its history """
        self.state = self.history[0]
        self.history.append(self.state)