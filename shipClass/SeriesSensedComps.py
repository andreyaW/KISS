""" This module contains the functions which is used to represent a group of series sensed components in the ship's systems. """

from shipClass.System import System

class SeriesSensedComps(System):
    occurence_num = 0

    def __init__(self, components, unmanned: bool = False):
        self.comps = components

        self.name = "SeriesSensedComps"
        # self.name = [comp.name for comp in components]
        self.states = components[0].comp.states  # Assuming all components have the same states

        # Initialize the parent System class 
        super().__init__(name = self.name, comps= self.comps, parallels=None, unmanned=unmanned) 