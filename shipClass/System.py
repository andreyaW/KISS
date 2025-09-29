from shipClass.Component import Component
from utils.helperFunctions import SolveStructureFunction, set_x_ticks
from utils.excelFunctions import grabSysTruthData, addTimeSteps, addTruth, highlightParallels, finalFormatting
from utils.SystemDiagram import SystemDiagram

import xlsxwriter
import matplotlib.pyplot as plt
import numpy as np


class System:
    def __init__(self, name, comps: list[Component], parallels=None, repairable: bool = False):
        """
        Model a system composed of multiple components (series and parallel).

        Parameters
        ----------
        name : str
            Name of the system.
        comps : list[Component]
            Components making up the system.
        parallels : list of tuple
            Parallel component sets (1-based indices).
        repairable : bool
            Whether the system is repairable.
        """
        self.name = name
        self.comps = comps
        self.parallels = parallels
        self.initialize(repairable)

# ------------------- Simulation Functions ----------------
    def initialize(self, repairable: bool = False):
        for comp in self.comps:
            comp.initialize(repairable)

        # initial system state
        self.history = SolveStructureFunction(self.comps, self.parallels)
        self.states = self.comps[0].states
        self.n = len(self.comps)

    def simulate(self, num_steps: int):
        """
        Vectorized system simulation over multiple steps.
        Each component simulates its own history, then the system state is computed vectorized.
        """
        for comp in self.comps:
            comp.simulate(num_steps)

        # compute system history vectorized
        self.history = np.append(self.history, SolveStructureFunction(self.comps, self.parallels, num_steps))

    def reset(self):
        """Reset system and all components to initial state."""
        for comp in self.comps:
            comp.reset()
        
        # assume initial system state is correct (all components operational)
        self.state = max(self.states.keys())
        self.history = np.array([self.state], dtype=int)
        
# -------------- Functions for Plotting --------------------------
    def plotHistory(self, plot_comp_history: bool = False, return_ax=False):
        fig, ax = plt.subplots()
        ax.plot(self.history, marker=',', label='System Truth')

        ax.set_ylabel('State')
        ax.set_yticks(list(self.states.keys()))
        ax.set_yticklabels(list(self.states.values()))
        ax.set_xlabel('Time Step')
        set_x_ticks(ax, len(self.history))
        ax.grid()
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  fancybox=True, shadow=True, ncol=5)

        if plot_comp_history:
            for comp in self.comps:
                ax.plot(comp.history, marker='o', linestyle='', label=comp.name.capitalize())
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                      fancybox=True, shadow=True, ncol=5)

        if return_ax:
            return ax

    def drawSystem(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots()

        sys_diagram = SystemDiagram(ax=ax)
        spacing = 1
        comp_size = 2
        sys_diagram.defineLocations(self, comp_size, spacing)

        for comp in self.comps:
            x, y = sys_diagram.comp_locations[comp]
            sys_diagram.drawComp(comp, x, y, comp_size)

        sys_diagram.drawConnections(self, comp_size)
        sys_diagram.displayDiagram()

# --------------- Functions for Printing to Excel ----------------
    def check4DuplicateNames(self):
        seen = set()
        for comp in self.comps:
            if comp.name in seen:
                i = 1
                new_name = f"#{i+1} {comp.name}"
                while new_name in seen:
                    i += 1
                    new_name = f"#{i+1} {comp.name}"
                comp.name = new_name

                if not isinstance(comp, Component):
                    for i, sub_comp in enumerate(comp.comps):
                        sub_comp.name = f"#{i+1} {sub_comp.name}"
            seen.add(comp.name)

    def printHistory2Excel(self, filename='system_history.xlsx', worksheet=None, addComps: bool = True):
        """
        Print the system and all component histories to Excel using vectorized writes.

        Parameters
        ----------
        filename : str
            Excel file name.
        worksheet : xlsxwriter worksheet
            Optional pre-created worksheet.
        addComps : bool
            Whether to include component histories.
        """
        self.check4DuplicateNames()

        with xlsxwriter.Workbook(filename) as workbook:
            # Create main worksheet
            if worksheet is None:
                sheet_name = self.name[:31]
                worksheet = workbook.add_worksheet(sheet_name)

            num_steps = len(self.history)

            # Write time steps in column A
            worksheet.write(0, 0, "Time Step")
            worksheet.write_column(1, 0, np.arange(num_steps))

            # Write system truth states in column B
            worksheet.write(0, 1, "System Truth State")
            worksheet.write_column(1, 1, self.history)

            if addComps:
                for comp in self.comps:
                    self._writeComponentToExcel(comp, workbook, num_steps)

        finalFormatting(worksheet, self.n)

# ---------------------- Helper Method ----------------------
    def _writeComponentToExcel(self, comp, workbook, num_steps):
        """
        Write a single component (or SeriesComps) history to a new worksheet.
        Handles SeriesComps recursively.
        """
        sheet_name = comp.name[:31]  # Excel sheet name max 31 chars
        ws = workbook.add_worksheet(sheet_name)

        # Write time steps
        ws.write(0, 0, "Time Step")
        ws.write_column(1, 0, np.arange(num_steps))

        # Write component history
        ws.write(0, 1, f"{comp.name.capitalize()} Truth State")
        ws.write_column(1, 1, comp.history)

        # If the component is a SeriesComps, recursively write its subcomponents
        if hasattr(comp, 'comps') and isinstance(comp.comps, list):
            for sub_comp in comp.comps:
                self._writeComponentToExcel(sub_comp, workbook, num_steps)