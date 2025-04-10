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

    return modes[0] # If there are multiple modes, return the first only
    