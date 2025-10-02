from shipClass.SensedSystem import SensedSystem
from shipClass.Ship import Ship
from utils.helperFunctions import SolveStructureFunction, set_x_ticks
from utils.excelFunctions import addTruth, addTimeSteps, addSensed, highlightParallels, finalFormatting

import matplotlib.pyplot as plt
import xlsxwriter
import numpy as np

class SensedShip():
    def __init__(self, ship: Ship, sensors: list[tuple[int, str]] = None):
        self.ship = ship
        self.sensedState = self.ship.state
        self.sensedHistory = [self.sensedState]
        self.sensedSystems = []
        self.sensors = sensors
        self.attach_sensors()

    # ---------------------- Initialization Functions -----------------------------
    def attach_sensors(self):
        """ Attach sensors to each system in the ship. """
        if self.sensors is None:
            self.sensors = [[(3, 'Good') for comps in system.comps] for system in self.ship.systems.values()]

        shipSystems = list(self.ship.systems.values())
        for i, shipSystem in enumerate(shipSystems):
            sensedSystem = SensedSystem(shipSystem, self.sensors[i])
            self.sensedSystems.append(sensedSystem)
        self.n = len(self.sensedSystems)

    # -------------------- Simulation Functions -----------------------------
    def simulate(self, time_steps):
        ''' simulate the ship and all its sensed systems for a number of time steps '''
        # simulate each sensed system of the ship
        for sensedSystem in self.sensedSystems:
            sensedSystem.simulate(time_steps)

        # update the truth state of the ship
        self.ship.history = np.concatenate([self.ship.history, SolveStructureFunction(list(self.ship.systems.values()), self.ship.parallels, time_steps)])
        self.ship.state = self.ship.history[-1]
        
        # update the sensed state of the ship
        self.sensedHistory = np.concatenate([self.sensedHistory, SolveStructureFunction(self.sensedSystems, self.ship.parallels, time_steps, sensed=True)])
        self.sensedState = self.sensedHistory[-1]

    def reset(self):
        # reset each sensed system of the ship
        for sensedSystem in self.sensedSystems:
            sensedSystem.reset()

        # reset the history of the true ship (assume initial ship state (all systems operational))
        self.ship.state = max(self.ship.states.keys())
        self.ship.history = np.array([self.ship.state], dtype=int)
  
        # reset the sensed history of the ship (assume initial sensed state is correct)
        self.sensedState = self.ship.state
        self.sensedHistory = np.array([self.sensedState], dtype=int)

    # ---------------------- Plotting and Printing Functions -----------------------------
    def plotHistory(self):
        # Plot the true history of the ship
        ax = self.ship.plotHistory(return_ax=True)

        # Plot the sensed history of the ship
        ax.plot(self.sensedHistory, marker=',', label='Sensed', linestyle='--', linewidth=1, color='orange')

        # add updated legend and show fig
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  fancybox=True, shadow=True, ncol=5)
        plt.show()


    def printHistory2Excel(self, filename: str, worksheet= None, addComps: bool = False) -> None:
        """ Print the history of the ship and its systems to an excel file """

        # add to the workbook using xlsxwriter
        with xlsxwriter.Workbook(filename) as workbook:
            
            # if no worksheet is provided, create a new workbook and worksheet
            if worksheet is None:
                worksheet = workbook.add_worksheet(self.ship.name) 
            
            # add data to the worksheet
            num_data = len(self.ship.history)
            systems = list(self.sensedSystems)
            for i in range(num_data):

                # add the time steps to the first column
                addTimeSteps(workbook, worksheet,i)

                # grab truth data for step i 
                truth_data = [self.ship.history[i]] + [systems[j].system.history[i] for j in range(self.n)] 

                # on step zero add headers to the top row then first row of data
                if i==0: 
                    ship_truth_headers = [f'Ship Truth State'] + [f'System {i+1} Truth State' for i in range(self.n)]
                    addTruth(workbook, worksheet, i, truth_data, ship_truth_headers)
                # for remaining steps add data to the row
                else: 
                    addTruth(workbook, worksheet, i, truth_data)

                # grab sensed data for step i
                sensed_data = [self.sensedHistory[i]] + [systems[j].sensedHistory[i] for j in range(self.n)]
                # on step zero add headers to the top row then first row of data
                if i==0: 
                    ship_sensed_headers = [f'Ship Sensed State'] + [f'System {i+1} Sensed State' for i in range(self.n)]
                    addSensed(workbook, worksheet, i, sensed_data, ship_sensed_headers)

                # for remaining steps add data to the row
                else: 
                    addSensed(workbook, worksheet, i, sensed_data)

            # add formating for parallel components
            if self.ship.parallels is not None:
                highlightParallels(workbook, worksheet, self.ship.parallels, num_data, self.n)
            
            finalFormatting(worksheet, self.n)       

            if addComps:
                # add each systems data to their own worksheet
                for i in range(self.n):
                    systems[i].system.check4DuplicateNames()  # ensure no duplicate names in each sensed system

                    for comps in systems[i].sensedComps: 
                        if type(comps) is SensedSystem:
                            sub_sys = comps

                            # add the systems sub system to their own worksheet
                            sheet_name = f'System {i+1}- ' + sub_sys.system.name.capitalize()
                            ws = workbook.add_worksheet(sheet_name[:31])
                            sub_sys.printHistory2Excel(filename, worksheet=ws, addComps=True)

                            # add each component in the series to their own worksheet
                            for comp in sub_sys.sensedComps:
                                sheet_name = f'System {i+1}- ' + comp.comp.name.capitalize()
                                ws = workbook.add_worksheet(sheet_name[:31])
                                comp.printHistory2Excel(filename, worksheet=ws)
                        else:
                            # add the component to its own worksheet
                            sheet_name = f'System {i+1}-' + comps.comp.name.capitalize()
                            ws = workbook.add_worksheet(sheet_name[:31])
                            comps.printHistory2Excel(filename, worksheet=ws)

                    # create a new worksheet for each system
                    ws = workbook.add_worksheet(f'System {i+1} History')

                    # add the history of the system to the worksheet
                    systems[i].printHistory2Excel(filename, ws, addComps=True)