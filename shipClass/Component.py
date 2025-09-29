import numpy as np
import matplotlib.pyplot as plt
import xlsxwriter
from shipClass.MarkovChain import MarkovChain
from utils.excelFunctions import finalFormatting

class Component(MarkovChain):
    def __init__(self, 
                 name: str = "Component", 
                 MTTF: float = 50,
                 MTTR='NR',
                 states: dict = {0: 'major failure', 
                                 1: 'incipient failure/alert', 
                                 2: 'working'}) -> None:
        self.MTTF = MTTF
        self.MTTR = MTTR
        self.states = states
        self.name = name 
        self.history = np.array([], dtype=int)
        self.state = list(self.states.keys())[-1]

    def defineTwoStateTransitionMatrix(self, repairable: bool = False):
        fail_rate = 1 / self.MTTF
        repair_rate = 0 if not repairable or self.MTTR=='NR' else 1/self.MTTR
        return np.array([[1 - repair_rate, repair_rate],
                         [fail_rate, 1 - fail_rate]])

    def defineThreeStateMatrix(self, repairable: bool = False):
        lambda_ = 1/self.MTTF
        lambda_d = lambda_ * np.random.rand()
        lambda_f = lambda_ - lambda_d
        mu_ = 0 if not repairable or self.MTTR=='NR' else 1/self.MTTR
        T = np.zeros((3,3))
        T[0,0] = 1
        T[1,1] = 1 - mu_
        T[1,2] = mu_
        T[2,0] = lambda_f
        T[2,1] = lambda_d
        T[2,2] = 1 - (lambda_d + lambda_f)
        return T

    def initialize(self, repairable: bool = False):
        num_states = len(self.states)
        if num_states == 3:
            self.transition_matrix = self.defineThreeStateMatrix(repairable)
        else:
            self.transition_matrix = self.defineTwoStateTransitionMatrix(repairable)
        super().__init__(self.states, self.transition_matrix)
        self.history = np.array([self.state], dtype=int)

    def simulate(self, num_steps=1):
        states = np.array(list(self.states.keys()))
        history = np.empty(num_steps, dtype=int)

        state = self.state
        for i in range(num_steps):
            state = np.random.choice(states, p=self.transition_matrix[state])
            history[i] = state

        self.state = state
        self.history = np.concatenate([self.history, history])
        
    def reset(self):
        self.state = max(self.states.keys())
        self.history = np.array([self.state], dtype=int)

    def plotHistory(self):
        fig, ax = plt.subplots()
        ax.plot(self.history, marker='o', linestyle='-', label=self.name)
        ax.set_ylabel('State')
        ax.set_xlabel('Time Step')
        ax.legend()
        return ax

    def printHistory2Excel(self, filename: str, worksheet=None):
        with xlsxwriter.Workbook(filename) as workbook:
            if worksheet is None:
                worksheet = workbook.add_worksheet(self.name[:31])
            num_data = len(self.history)
            worksheet.write(0, 0, "Time Step")
            worksheet.write_column(1, 0, np.arange(num_data))
            worksheet.write(0, 1, "Comp Truth State")
            worksheet.write_column(1, 1, self.history)
            finalFormatting(worksheet, 1)
