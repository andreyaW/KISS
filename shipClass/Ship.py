from shipClass.System import System
from shipClass.SeriesComps import SeriesComps
from shipClass.Component import Component
from utils.helperFunctions import SolveStructureFunction, set_x_ticks
from utils.excelFunctions import addTruth, addTimeSteps, highlightParallels, finalFormatting

import matplotlib.pyplot as plt
import pandas as pd
import xlsxwriter
import ast
import numpy as np


class Ship:

    def __init__(self, name, excel_file, repairable: bool = True, np_rng_num: int = 0)-> None:
        """Initialize ship with name, Excel data, and repairable status."""
        self.name = name
        self.repairable = repairable
        self.initializeShipSystemsfromExcel(excel_file, self.repairable, np_rng_num)

# ------------ Simulation Functions -------------------

    def initializeShipSystemsfromExcel(self, excel_file, repairable: bool, np_rng_num: int = 0):
        """Read Excel and initialize systems and components."""
        
        # Read machinery reliability
        rel_df = pd.read_excel(excel_file, sheet_name=0)

        # Read system structure
        sys_structure_df = pd.read_excel(excel_file, sheet_name=1)
        sys_structure_df['Structure'] = sys_structure_df['Structure'].apply(ast.literal_eval)

        # Read overall ship structure (parallel systems)
        ship_structure_df = pd.read_excel(excel_file, sheet_name=2)
        ship_structure_df['ship structure'] = ship_structure_df['ship structure'].apply(ast.literal_eval)
        self.parallels = ship_structure_df.iat[0, 0]

        # Close any open Excel files
        pd.ExcelFile(excel_file).close()

        # Initialize systems
        ship_systems = {}
        for i, sys_struct in enumerate(sys_structure_df.Structure):
            sys_comps = []
            sys_parallels = []

            for comp in sys_struct:
                if isinstance(comp, int):
                    comp_name = rel_df.Component[comp]
                    comp_MTTF = rel_df.MTBF[comp]
                    comp_MTTR = rel_df.MTTR[comp]
                    sys_comps.append(Component(comp_name, comp_MTTF, comp_MTTR))

                elif isinstance(comp, tuple):
                    parallel_set = list(comp)
                    for j, idx in enumerate(parallel_set):
                        if isinstance(idx, int):
                            comp_name = rel_df.Component[idx]
                            comp_MTTF = rel_df.MTBF[idx]
                            comp_MTTR = rel_df.MTTR[idx]
                            c = Component(comp_name, comp_MTTF, comp_MTTR)
                            sys_comps.append(c)
                            parallel_set[j] = c
                        elif isinstance(idx, list):
                            series_set_comps = []
                            for k, idx2 in enumerate(idx):
                                if isinstance(idx2, int):
                                    comp_name = rel_df.Component[idx2]
                                    comp_MTTF = rel_df.MTBF[idx2]
                                    comp_MTTR = rel_df.MTTR[idx2]
                                    series_set_comps.append(Component(comp_name, comp_MTTF, comp_MTTR))
                            series_set = SeriesComps(components=series_set_comps)
                            sys_comps.append(series_set)
                            parallel_set[j] = series_set
                    # replace parallel_set with their 1-based positions
                    parallel_set = tuple([sys_comps.index(c) + 1 for c in parallel_set])
                    sys_parallels.append(parallel_set)

            sys_name = sys_structure_df.System[i]
            if sys_parallels:
                ship_systems[sys_name] = System(sys_name, sys_comps, sys_parallels, repairable=repairable)
            else:
                ship_systems[sys_name] = System(sys_name, sys_comps, repairable=repairable)

        self.systems = ship_systems
        self.n = len(self.systems)
        self.states = list(ship_systems.values())[0].states
        self.state = max(self.states.keys())                            # initial ship state
        self.history = np.array([self.state], dtype=int)

# ------------ Vectorized Simulation -------------------

    def simulate(self, num_steps: int):
        """Vectorized simulation of all systems and ship state."""
        systems = list(self.systems.values())
        for sys in systems:
            sys.simulate(num_steps)

        # Vectorized ship history
        self.history = np.concatenate([self.history, SolveStructureFunction(systems, self.parallels, num_steps)])

    def reset(self):
        """Reset ship and all systems to initial state."""
        for sys in self.systems.values():
            sys.reset()
        
        # assume initial ship state is correct (all systems operational)
        self.state = max(self.states.keys())
        self.history = np.array([self.state], dtype=int)
        
# ------------ Plotting Functions -------------------

    def plotHistory(self, return_ax=False):
        fig, ax = plt.subplots()
        ax.plot(self.history, marker=',', linewidth=2, label='Ship Truth')
        ax.set_ylabel('State')
        ax.set_yticks(list(self.states.keys()))
        ax.set_yticklabels(list(self.states.values()))
        ax.set_xlabel('Time Step')
        set_x_ticks(ax, len(self.history))
        ax.grid()
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  fancybox=True, shadow=True, ncol=5)
        if return_ax:
            return ax

# ------------ Vectorized Excel Export -------------------
    def printHistory2Excel(self, filename: str, addComps: bool = True):
        """
        Print ship and all system/component histories to Excel using vectorized writes.
        Ensures unique worksheet names.
        """
        systems = list(self.systems.values())
        num_steps = len(self.history)
        used_sheet_names = set()

        with xlsxwriter.Workbook(filename) as workbook:
            # ---------------- Main Ship Worksheet ----------------
            ws_ship = workbook.add_worksheet(self.name[:31])
            used_sheet_names.add(self.name[:31])

            # Time steps
            ws_ship.write(0, 0, "Time Step")
            ws_ship.write_column(1, 0, np.arange(num_steps))

            # Ship truth states
            ws_ship.write(0, 1, "Ship Truth State")
            ws_ship.write_column(1, 1, self.history)

            # Systems truth states
            for j, sys in enumerate(systems):
                col = j + 2
                ws_ship.write(0, col, f"System {j+1} Truth State")
                ws_ship.write_column(1, col, sys.history)

            # Highlight parallel systems if any
            if self.parallels is not None:
                highlightParallels(workbook, ws_ship, self.parallels, num_steps, self.n)

            finalFormatting(ws_ship, self.n)

            # ---------------- Component Worksheets ----------------
            if addComps:
                for j, sys in enumerate(systems):
                    sys.check4DuplicateNames()
                    for comp in sys.comps:
                        self._writeComponentWorksheet(comp, workbook, f"System {j+1}-", num_steps, used_sheet_names)

        # close the workbook to save changes
        workbook.close()

    # ---------------------- Helper Method ----------------------
    def _writeComponentWorksheet(self, comp, workbook, prefix, num_steps, used_sheet_names):
        """
        Write a single component or SeriesComps to a worksheet.
        Ensures unique worksheet names across the workbook.
        """
        # Generate unique sheet name
        base_name = f"{prefix} {comp.name}"[:31]
        sheet_name = base_name
        i = 1
        while sheet_name in used_sheet_names:
            suffix = f"_{i}"
            sheet_name = base_name[:31-len(suffix)] + suffix
            i += 1
        used_sheet_names.add(sheet_name)

        ws = workbook.add_worksheet(sheet_name)

        # Time steps
        ws.write(0, 0, "Time Step")
        ws.write_column(1, 0, np.arange(num_steps))

        # Component history
        ws.write(0, 1, f"{comp.name.capitalize()} Truth State")
        ws.write_column(1, 1, comp.history)

        # Recursively handle SeriesComps
        if hasattr(comp, 'comps') and isinstance(comp.comps, list):
            for sub_comp in comp.comps:
                self._writeComponentWorksheet(sub_comp, workbook, sheet_name, num_steps, used_sheet_names)