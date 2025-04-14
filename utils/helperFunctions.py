def get_key_by_value(my_dict, value):
        """
        Returns the key associated with the given value in the dictionary.
        If the value is not found, it returns None. If multiple keys have the same value,
        it returns the first key found.
        """
        for key, val in my_dict.items():
            if val == value:
                return key
        return None
    
    
def find_mode(data):
    counts = {}
    for item in data:
        if item in counts:
            counts[item] += 1
        else:
            counts[item] = 1

    max_count = 0
    modes = []
    for item, count in counts.items():
        if count > max_count:
            modes = [item]
            max_count = count
        elif count == max_count:
            modes.append(item)
            
        if max_count == 1:
            return min(data) # If all values are unique, return the minimum value

    return modes[0] # If there are multiple modes, return the first only


def getStates(list_of_objs, bool = False) -> list:     
    """gets the states of the systems components """
    
    states = []  # list to store all states       
    
    # if bool is True, get the TRUE states of the components
    if bool: 
        for i, obj in enumerate(list_of_objs):
            states.append(obj.state)   
        return states
    
    # if bool is False, get the SENSED states of the components 
    else: 
        for i,obj in enumerate(list_of_objs):
            states.append(obj.sensedState)   
            
        return states

    
def SolveStructureFunction(objects, parallels: list[tuple],  bool = False) -> int:
    ''' calculate the structure function of either a system of sensed components or a ship of systems '''
    
    Xi = getStates(objects, bool)  # state vector (stores the state of each object in the objects list) 
        
    # do the math on the parallel sets first
    if parallels is not None: 
        for parallel_set in parallels:
            
            #subtract 1 from each value to get the idx
            parallel_set = [i-1 for i in parallel_set]
            parallels_states = [0 for i in parallel_set]  
            for i, comp_idx in enumerate(parallel_set):
                parallels_states[i] = Xi[comp_idx]        # get the state of each component in the parallel set 
                
                # remove the states from the state vector
                Xi[comp_idx] = None
            
            # determine the state of the set using structure function and add it to the state vector 
            Xi_parallels = max(parallels_states) 
            Xi.append(Xi_parallels)
        
    # now finish the math on the series components
    phi = min(Xi)                
    return phi





    # if parallels is not None:
        
    #     for parallel_sets in parallels:
            
    #         #subtract 1 from each value to get the idx
    #         parallel_sets = [i-1 for i in parallel_sets]
    #         states = getStates(parallel_sets,bool)
            
    #         # determine the state of the set using structure function then, 
    #         Xi_parallels = max(states) 
            
    #         # add the state of the parallel sets to overall system list
    #         Xi.append(Xi_parallels)      
                    
    # # considering all other components in series
    # series_comps = []  # list to store the states of series components            

    # # if there are components in parallel, get the idx of the series components
    # if self.parallels is not None: 
    #     for i in range(len(self.comps)):
    #         if i not in self.parallels:
    #             series_comps.append(i)  
    # # else get the idx of all components
    # else:
    #     series_comps = list(range(len(self.comps)))  # get the index of all components
    
    # # double checking there are some series components to add to the structure function
    # if series_comps != []:
    #     Xi = Xi + self.getStates(series_comps, bool)
    # else:
    #     pass # all comps must have been in a parallel set
    
    # # final series consideration (parallel sets and series components)
    # phi = min(Xi)               
    # return phi