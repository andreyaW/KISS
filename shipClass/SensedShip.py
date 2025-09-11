from shipClass.SensedSystem import SensedSystem
from shipClass.Ship import Ship
from utils.helperFunctions import SolveStructureFunction, set_x_ticks
from utils.excelFunctions import addTruth, addTimeSteps, addSensed, highlightParallels, finalFormatting

import matplotlib.pyplot as plt
import xlsxwriter

class SensedShip():
    def __init__(self, ship: Ship, number_of_sensors: list[int] = None):
        self.ship = ship
        self.sensedState = self.ship.state
        self.history = [self.sensedState]
        self.sensedSystems = []

    def attach_sensors(self, number_of_sensors: list[int] = None):
        """ Attach sensors to each system in the ship. """        
        self.number_of_sensors = number_of_sensors
        if self.number_of_sensors is None:
            self.number_of_sensors = [[3 for i in range((len(shipSystems.comps)))] for shipSystems in self.ship.systems.values()]
        else: 
            self.number_of_sensors = number_of_sensors

        shipSystems = list(self.ship.systems.values())
        for i, shipSystem in enumerate(shipSystems):
            print(f"The system has {len(shipSystem.comps)} components")
            print(f"Attaching {len(self.number_of_sensors[i])} sets of sensors to system")
            sensedSystem = SensedSystem(shipSystem, self.number_of_sensors[i])
            self.sensedSystems.append(sensedSystem)
        self.n = len(self.sensedSystems)

    def simulate(self, time_step):
        for i in range(time_step):
            for sensedSystem in self.sensedSystems:
                sensedSystem.simulate(1)

            # update the truth state of the ship
            self.ship.update_state()

            # determine the sensed state of the ship
            self.sensedState = SolveStructureFunction(self.sensedSystems, self.ship.parallels, sensed=True)
            self.history.append(self.sensedState)


    def reset(self):
        self.history = [self.sensedState]
        for sensedSystem in self.sensedSystems:
            sensedSystem.reset()

    def determineFailureTime(self):
        # Determine the failure time of the ship
        # first time the state = 0
        return self.ship.history.index(0)

    def plotHistory(self):
        # Plot the true history of the ship
        ax = self.ship.plotHistory(return_ax=True)

        # Plot the sensed history of the ship
        ax.plot(self.history, marker=',', label='Sensed', linestyle='--', color='orange')

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
                sensed_data = [self.sensedState] + [systems[j].sensedState for j in range(self.n)]
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

            # if addComps:
            #     # add each systems data to their own worksheet
            #     for i in range(self.n):

            #         for comps in systems[i].comps: 
            #             if type(comps) is SensedSystem:
            #                 # add the systems sub system to their own worksheet
            #                 ws = workbook.add_worksheet(f'System {i+1}- ' + comps.name.capitalize())
            #                 comps.printHistory2Excel(filename, worksheet=ws, addComps=True)

            #                 # add each component in the series to their own worksheet                        
            #                 for comp in comps.components:
            #                     ws = workbook.add_worksheet(f'System {i+1}- {comp.name.capitalize()}')
            #                     comp.printHistory2Excel(filename, worksheet=ws)
            #             else:
            #                 ws = workbook.add_worksheet(f'System {i+1}- {comps.name.capitalize()}')
            #                 comps.printHistory2Excel(filename, worksheet=ws)

            #                             # create a new worksheet for each system

            #         ws = workbook.add_worksheet(f'System {i+1} History')

            #         # add the history of the system to the worksheet
            #         systems[i].printHistory2Excel(filename, ws, addComps=True)