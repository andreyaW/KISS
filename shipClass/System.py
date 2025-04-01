class System():
    ''' a simple model of a system '''

    def __init__(self, comps)-> None:
        
        
        self.components = comps
        self.state = determineSysState()
        self.history = []
        
        
    def determineSysState(self):
        ''' determine the state of the system based on the states of its components '''
    
    
    