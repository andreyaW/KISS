from shipClass.SensedSystem import SensedSystem
from shipClass.Ship import Ship
from utils.helperFunctions import SolveStructureFunction, set_x_ticks
from utils.excelFunctions import addTruth, addTimeSteps, addSensed, highlightParallels, finalFormatting

import matplotlib.pyplot as plt
import xlsxwriter

class SensedShip():
    def __init__(self, ship: Ship, sensors: list[tuple[int, str]] = None):
        self.ship = ship
        self.sensedState = self.ship.state
        self.sensedHistory = [self.sensedState]
        self.sensedSystems = []
        self.sensors = sensors

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
    def simulate(self, time_step):
        for i in range(time_step):
            for sensedSystem in self.sensedSystems:
                sensedSystem.simulate(1)

            # update the truth state of the ship
            self.ship.update_state()

            # determine the sensed state of the ship
            self.sensedState = SolveStructureFunction(self.sensedSystems, self.ship.parallels, sensed=True)
            self.sensedHistory.append(self.sensedState)

    def reset(self):
        # reset the true ship to initial conditions
        self.ship.reset()
        
        # reset sensed ship to initial conditions
        self.sensedHistory = [self.sensedState]
        for sensedSystem in self.sensedSystems:
            sensedSystem.reset()
        self.sensedState = self.ship.state

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

    # ---------------------- Additional Analysis Functions -----------------------------

    def determineFirstFailureTime(self):
        # Determine the failure time of the ship
        # first time the state = 0
        return self.ship.history.index(0)
        
    def calculate_state_accuracy(self):
        true_states = self.ship.history
        sensed_states = self.sensedHistory
        correct = sum(t == s for t, s in zip(true_states, sensed_states))

        return correct / len(true_states) if true_states else 0



    def getFalseAlarmRate(self):
        """ Calculate the false alarm rate of the ship. 
            False alarm rate is defined as the number of times the ship is sensed to be failed when it is actually working,
            divided by the total number of times the ship is sensed to be failed.
        """
        false_alarms = 0
        total_alarms = 0

        for true_state, sensed_state in zip(self.ship.history, self.sensedHistory):
            if sensed_state == 0 or sensed_state == 1:  # Sensed as failed or incipient failure
                total_alarms += 1
                if true_state == 1:  # Actually working
                    false_alarms += 1

        return (false_alarms / total_alarms) * 100 if total_alarms > 0 else 0

    def getUnexpectedFailureRate(self):
        """ Calculate the number of unexpected failures of the ship.
            Unexpected failure is defined as the number of times the ship actually fails when it is sensed to be working,
            divided by the total number of times the ship actually fails.
        """
        unexpected_failures = 0
        total_failures = 0

        for true_state, sensed_state in zip(self.ship.history, self.sensedHistory):
            if true_state == 0:  # Actually failed
                total_failures += 1
                if sensed_state == 2:  # Sensed as working
                    unexpected_failures += 1

        return (unexpected_failures / total_failures) * 100 if total_failures > 0 else 0