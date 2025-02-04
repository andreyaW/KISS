import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


class MarkovChain:
    def __init__(self):
        
        self.history = []
        self.states = []
        self.transitionMatrix = []
        
    def draw(self):
        
        # Create the Markov Chain as a directed graph
        G = nx.DiGraph()

        # Add edges based on transition matrix
        for i in range(len(self.states)):
            for j in range(len(self.states)):
                G.add_edge(self.states[i], self.states[j], weight=self.transitionMatrix[i][j])

        # Define positions for states arranged in a straight line
        pos = {self.states[i]: (i, 0) for i in range(len(self.states))}

        # Draw the graph with the defined positions
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue')

        # Draw edge labels with transition weights
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        
        # Show the plot
        plt.show()

    def setupMarkovChain(self, states, transitionMatrix):
        self.states = states
        self.transitionMatrix = transitionMatrix
        self.draw()    

        initial_state = states[0]
        self.history.append(initial_state)

    def currentState(self):
        return self.history[-1]

    def simulate(self, steps):
        # Simulate the Markov Chain
        for i in range(steps):
            states = list(self.states.keys())
            state_names = list(self.states.values())
            
            currentState = self.currentState()  # name of the current state
            currentState_idx = list(self.states.values()).index(currentState)
                       
            next_state_idx = np.random.choice(states, p=self.transitionMatrix[currentState_idx])
            next_state = state_names[next_state_idx]        
            self.history.append(next_state)
            
            # if the current state is the first ocurance of a failure, store the time
            if currentState == state_names[-1] and self.history[-2] != state_names[-1]:
                self.failure_time = i

# ---------------------- Example ---------------------- 