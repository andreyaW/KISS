from shipClass.sensedComp import sensedComp
from KISS.Miantainer import maintainer
from KISS.costFunction import costFunction


class MDP(sensedComp, maintainer, costFunction):
    
    def __init__ (self, 
                  sensedComp : sensedComp,
                  maintainer : maintainer,
                  costFunction : costFunction) -> None:
        
        """ Initialize the MDP """
        
        self.sensedComp = sensedComp       # sensed component
        self.maintainer = maintainer       # maintainer
        self.costFunction = costFunction
        
        self.state = sensedComp.state               # true state of the sensed component
        self.sensed_state = sensedComp.sensedState  # sensed state of the component