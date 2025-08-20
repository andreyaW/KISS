from shipClass.System import System

class SeriesComps(System):

    def __init__(self, components, repairable: bool = False):

        """ group of series components represented as a subsystem for larger systems
        
            Parameters
            ----------
            components: list
                A list of component objects that are part of this subsystem.
            repairable: bool
                A flag indicating whether the subsystem is unmanned (default is False).
            """

        self.comps = components
        self.name = "SeriesComps"
        self.name = str([comp.name for comp in components])
        self.states = components[0].states  # Assuming all components have the same states

        # Initialize the parent System class 
        super().__init__(name = self.name, comps= self.comps, parallels=None, repairable=repairable) 
