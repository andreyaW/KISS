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
                                 2: 'working'},
                 np_rng_num: int = None) -> None:

        """ Initialize a Component with a Markov Chain model """    
        self.MTTF = MTTF
        self.MTTR = MTTR
        self.states = states

        if np_rng_num is None:
            self.rng = np.random.default_rng(0)  # default seed
        else:
            self.rng = np.random.default_rng(np_rng_num)

        self.name = name 
        self.history = np.array([], dtype=int)
        self.state = list(self.states.keys())[-1]

    def defineTwoStateTransitionMatrix(self, repairable: bool = False):
        fail_rate = 1 / self.MTTF
        repair_rate = 0 if not repairable or self.MTTR=='NR' else 1/self.MTTR
        return np.array([[1 - repair_rate, repair_rate],
                         [fail_rate, 1 - fail_rate]])


    def defineThreeStateMatrix(self, repairable: bool = False):
        """Define a 3-state Markov transition matrix (failed, degraded, working)
        adjusted so that the empirical MTTF ≈ input MTTF,
        with a random degradation fraction (0–30%)."""

        λ = 1 / self.MTTF
        μ = 0 if not repairable or self.MTTR == 'NR' else 1 / self.MTTR

        # Random fraction (0–30%) of failures that go through degradation
        p_deg = self.rng.uniform(0, 0.3)
        # p_min_2_maj_f= 0.  # fixed split for consistency

        # Split total failure rate
        λ_d = λ * p_deg                 # working → degraded
        λ_f = λ * (1 - p_deg)           # working → failed
        λ_df = λ_d                      # degraded → failed (kept similar scale)

        # Split repair rate
        μ_d = μ * p_deg                 # fixed split for consistency
        μ_f = μ - μ_d

        # Build transition matrix
        T = np.zeros((3, 3))
        # failed state
        T[0, 0] = 1 - μ_f               # stay failed
        T[0, 2] = μ_f                   # failed to working (major repair)

        # degraded state
        T[1, 0] = λ_df                  # degraded to failed (minor to major failure)
        T[1, 1] = 1 - (μ_d + λ_df)      # stay degraded
        T[1, 2] = μ_d

        # working state
        T[2, 0] = λ_f                   # working to failed (major failure)
        T[2, 1] = λ_d                   # working to degraded (minor failure)
        T[2, 2] = 1 - (λ_d + λ_f)       # stay working

        return T
    
    # def defineThreeStateMatrix(self, repairable: bool = False):

    #     # failure rates are split between degraded and failed states
    #     lambda_ = 1/self.MTTF
    #     lambda_d = lambda_ * .3  # fixed split for consistency
    #     lambda_f = lambda_ - lambda_d
    #     lambda_df = abs(lambda_f - lambda_d)

    #     # repair rate
    #     mu_ = 0 if not repairable or self.MTTR=='NR' else 1/self.MTTR
    #     mu_d = mu_ * #self.rng.random()  # fixed split for consistency
    #     mu_f = mu_ - mu_d

    #     # setting transition matrix
    #     T = np.zeros((3,3))
    #     T[0,0] = 1-mu_f                     # stay failed
    #     T[0,2] = mu_f                       # failed to working (major repair)
    #     T[1,0] = lambda_df                  # degraded to failed (minor to major failure)
    #     T[1,1] = 1 - (mu_d + lambda_df)     # stay degraded
    #     T[1,2] = mu_d                       # degraded to working (minor repair)
    #     T[2,0] = lambda_f                   # working to failed (major failure)
    #     T[2,1] = lambda_d                   # working to degraded (minor failure)
    #     T[2,2] = 1 - (lambda_d + lambda_f)  # stay working

    #     return T
    
    def initialize(self, repairable: bool = False):
        num_states = len(self.states)
        if num_states == 3:
            self.transition_matrix = self.defineThreeStateMatrix(repairable)
        else:
            self.transition_matrix = self.defineTwoStateTransitionMatrix(repairable)
        super().__init__(self.states, self.transition_matrix, self.rng)
        self.history = np.array([self.state], dtype=int)

    def simulate(self, number_of_steps = 1):
        return super().simulate(number_of_steps)

    def reset(self):
        self.state = max(self.states.keys())
        self.history = np.array([self.state], dtype=int)

    def plotHistory(self):
        ax = super().plotHistory()
        ax.set_yticks(list(self.states.keys()))
        ax.set_yticklabels([self.states[key] for key in ax.get_yticks()])
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


    # ------- Useful for testing -------
    def calculateMTTF(self):
        """Calculate the empirical MTTF from the component's history,
        counting only *new* failure occurrences (not consecutive failed steps),
        and including the initial operational period before the first failure."""

        failed_state = 0  # adjust if your failed state uses a different code
        history = self.history

        # Detect transitions into and out of failure
        failure_onsets = np.where(
            (history == failed_state) &
            (np.concatenate(([True], history[:-1] != failed_state)))
        )[0]

        recovery_indices = np.where(
            (history != failed_state) &
            (np.concatenate(([False], history[:-1] == failed_state)))
        )[0]

        # No failures at all
        if len(failure_onsets) == 0:
            return self.MTTF

        times_between_failures = []

        # Include time from start to first failure
        times_between_failures.append(failure_onsets[0])

        # Pair each recovery with the next failure
        for rec in recovery_indices:
            next_failures = failure_onsets[failure_onsets > rec]
            if len(next_failures) > 0:
                times_between_failures.append(next_failures[0] - rec)

        # Compute mean time to failure
        self.MTTF = np.mean(times_between_failures) if times_between_failures else self.MTTF
        return self.MTTF


    def calculateMTTR(self):
        ''' Calculate the empirical MTTR from the component's history 
            repairs = sum(history[i-1] < history[i]) for i in range(1, len(history))
        '''
        
        # determine all instances where a repair has occurred
        repair_idxs = [i for i in range(1, len(self.history)) if self.history[i-1] < self.history[i]]
        num_repairs = len(repair_idxs)

        if num_repairs == 0:
            return self.MTTR  # no repairs occurred *******
        else:
            # for each repair, determine how long the component was down
            total_repair_time = 0
            for idx in repair_idxs:
                down_time = 0
                for j in range(idx-1, -1, -1):
                    if self.history[j] == self.history[idx-1]:  # still down
                        down_time += 1
                    else:
                        break
                total_repair_time += down_time

            # calculate MTTR
            self.MTTR = total_repair_time / num_repairs if num_repairs > 0 else 0
            return self.MTTR



        # # failure rates are split between degraded and failed states
        # lambda_ = 1/self.MTTF
        # lambda_d = lambda_ * self.rng.random()
        # lambda_f = lambda_ - lambda_d

        # # repair rate
        # mu_ = 0 if not repairable or self.MTTR=='NR' else 1/self.MTTR
        
        # # setting transition matrix
        # T = np.zeros((3,3))
        # T[0,0] = 1
        # T[1,1] = 1 - mu_
        # T[1,2] = mu_
        # T[2,0] = lambda_f
        # T[2,1] = lambda_d
        # T[2,2] = 1 - (lambda_d + lambda_f)
        # return T
