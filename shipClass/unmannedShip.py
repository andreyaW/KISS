from shipClass.Ship import Ship

class unmannedShip(Ship):

    def __init__(self, name, ship_data_file)-> None:
        """
        This class is used to simulate an unmanned ship subject to degradation over time and maintenance actions (PM only).
            Parameters
            ----------
            name: str
                The name of the ship.

            ship_data_file: str
                The path to the Excel file containing ship data.
        """
    
        self.repairable = False # This ship is unmanned so minor failures cannot be repaired
        super().__init__(name, excel_file=ship_data_file, repairable=self.repairable)
        # super().initializeShipSystemsfromExcel()











    # def conductPM(self, timeStep)-> None:
    #     '''
    #     This method conducts periodic maintenance on the ship's systems.
    #     It iterates through each system and performs maintenance actions as needed.
    #     '''
    #     # Conduct periodic maintenance on each system
    #     for sys in self.vessel.systems:
    #         periodicMaintenance(sys)

        