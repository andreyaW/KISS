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
        self.name = str([comp.name for comp in components])
        self.states = components[0].states  # Assuming all components have the same states

        # Initialize the parent System class 
        super().__init__(name = self.name, comps= self.comps, parallels=None, repairable=repairable) 

        self.MTTF = self.series_mttf()

    def series_mttf(self):
        """
        Compute the MTTF of components in series given their individual MTTFs.
        Assumes exponential lifetime distributions (constant failure rates).
            
        Returns:
            float: System MTTF
    
        """
        mttfs = [comp.MTTF for comp in self.comps]
        
        # Convert MTTFs to failure rates (λ = 1/MTTF)
        failure_rates = [1.0/m for m in mttfs]
        
        # System failure rate = sum of failure rates
        system_rate = sum(failure_rates)

        # System MTTF = 1 / system_rate
        system_MTTF = 1 / system_rate
        return system_MTTF
