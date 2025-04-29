import xlsxwriter
import textwrap

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
    
    # if bool is True, get the TRUE states of the objects
    if bool: 
        for i, obj in enumerate(list_of_objs):
            states.append(obj.state)   
        return states
    
    # if bool is False, get the SENSED states of the components 
    else: 
        for i,obj in enumerate(list_of_objs):
            states.append(obj.sensedState)         
        return states


def SolveStructureFunction(objects:list, parallels: list[tuple], bool = False) -> int:
    ''' calculate the structure function of either a system of sensed components or a ship of systems '''

    Xi_overall = []     # overall state vector
    Xi_temp = []        # state vector for each group considered

    # determine the state of each parallel set first
    if parallels is not None: 
        for parallel_sets in parallels:

            # subtract 1 from each value to get the idx
            parallel_sets = [i-1 for i in parallel_sets]
            parallel_objs = [objects[i] for i in parallel_sets]  # get the objects in the parallel set
            Xi_temp = getStates(parallel_objs,bool)          
            Xi_overall.append(max(Xi_temp))                      # add the state of the parallel sets to overall system list

    # determine the state of the series components
        # if parallels is None, all comps are in series
    if parallels is None: 
        series_comps_idx = list(range(len(objects)))
        series_objs = [objects[i] for i in series_comps_idx]  # get the objects in the series set
        Xi_temp = getStates(series_objs,bool)
        Xi_overall = Xi_overall + Xi_temp  # add the state of the series components to overall system list
    
    # if parallels is not None, get the idx of the series components
    else: 
        series_comp_idxs = []  # list to store the idx of series components
        objects_in_parallel = [i-1 for sublist in parallels for i in sublist]  # get all objects in parallel sets
        for i in range(len(objects)):
            if i not in objects_in_parallel:
                series_comp_idxs.append(i)
        series_objs = [objects[i] for i in series_comp_idxs]  # get the objects in the series set
        Xi_temp = getStates(series_objs,bool)  # get the states of the series components
        Xi_overall = Xi_overall + Xi_temp  # add the state of the series components to overall system list

    # final consideration of all states in overall system state vector
    phi = min(Xi_overall)               
    
    return phi


def idx2letter(idx):
    """ Convert an index to a letter (1 -> A, 2 -> B, etc.) """
    if idx < 1:
        raise ValueError("Index must be greater than or equal to 1")
    return chr(idx + 64)  # ASCII value of 'A' is 65

def wrap_text_in_box(ax, text, box_size, fontsize=8):
    """Wraps text to fit within a box of given size."""
    wrapped_text = '\n'.join(textwrap.wrap(text, width=int(box_size * 8), break_long_words=False)) # 8 letters per box size
    
    return wrapped_text