import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from utils.helperFunctions import get_key_by_value

class MarkovChain:
    def __init__(self, states: dict, transition_matrix: np.array, rng: int = None) -> None:
        """ Initialize the Markov Chain with the given states and transition matrix """
        self.states = states
        self.transitionMatrix = transition_matrix
        if rng is None:
            self.rng = np.random.default_rng(0)  # default seed
        else:
            self.rng = rng
        
        self.state = list(self.states.keys())[-1]     # initial state
        self.history = np.array([self.state])         # keep track of history as numpy array

# ---------------------- Monte Carlo Simulation  ----------------------       

    def simulate(self, number_of_steps: int = 1) -> None:
        """Simulate the Markov Chain over n steps using a fully vectorized method with RNG support."""
        cum_probs = np.cumsum(self.transitionMatrix, axis=1)

        # Array to store trajectory
        next_states = np.empty(number_of_steps, dtype=int)
        current_state = self.state

        # Generate all random values using the RNG
        random_vals = self.rng.random(number_of_steps)

        # Vectorized state propagation
        for i in range(number_of_steps):
            next_state = np.searchsorted(cum_probs[current_state], random_vals[i])
            next_states[i] = next_state
            current_state = next_state

        self.state = current_state
        self.history = np.concatenate((self.history, next_states))

    def reset(self):
        """ Reset the Markov Chain to its initial state and delete its history """
        self.state = self.history[0]
        self.history = np.array([self.state])

# ---------------------- Plotting Functions -----------------------------    
    def drawChain(self, name: str = None):
        """ Draw the Markov Chain as a directed graph """
        plt.figure()

        if name is not None:
            ax = plt.gca()
            ax.set_title(name)

        G = nx.DiGraph()
        for i in range(len(self.states)):
            for j in range(len(self.states)):
                G.add_edge(self.states[i], self.states[j], weight=self.transitionMatrix[i][j])

        pos = {self.states[i]: (i, 0) for i in range(len(self.states))}
        pos[self.states[0]] = (i + 1, -1)

        nx.draw(
            G, pos, with_labels=True, node_size=2000, node_color='skyblue', alpha=0.3,
            arrowsize=60, arrowstyle='-', font_size=10, font_weight='bold'
        )
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    def plotHistory(self):
        """ Plot the history of the Markov Chain """
        fig, ax = plt.subplots()
        ax.plot(self.history, marker='o', label='Truth State')
        ax.set_title('Markov Chain History')
        ax.set_xlabel('Time Step')
        ax.set_ylabel('State')

        y_ticks = list(self.states.keys())
        y_labels = [self.states[i] for i in y_ticks]
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)

        return ax


# ---------------------- Useful Methods  ----------------------       

    # def get_failure_time(self):
    #     """ Determine from the history when the object fails """
    #     failure_state = list(self.states.keys())[0]

    #     indices = np.where(self.history == failure_state)[0]
    #     if indices.size > 0:
    #         self.failure_time = indices[0]
    #         return self.failure_time
    #     return None