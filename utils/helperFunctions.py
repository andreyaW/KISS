from collections import Counter

import shutil
import os
import textwrap
import numpy as np
import tabulate

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

def find_mode(values):
    """Return the most frequent value in a list or 1D numpy array (fast)."""
    values = np.ravel(values)  # flatten if needed
    if values.size == 0:
        return None

    # If values are integers or booleans → use bincount (fastest)
    if np.issubdtype(values.dtype, np.integer) or values.dtype == bool:
        counts = np.bincount(values)
        return np.argmax(counts)

    # For general numeric or categorical values → use np.unique with counts
    unique_vals, counts = np.unique(values, return_counts=True)
    return unique_vals[np.argmax(counts)]


def reset(obj):
    """Resets the component to its initial state and deletes its history."""
    obj.state = obj.history[0]
    obj.history = [obj.state]


# Pick the right history accessor
def get_history(obj, num_steps: int, sensed: bool = False) -> np.ndarray:
    """ Returns the last num_steps of history from either the true state or sensed state. """
    if sensed:
        if not hasattr(obj, 'sensedHistory'):
            raise ValueError(f"get_history: Object of type {type(obj)} does not have sensedHistory attribute.") 
        return obj.sensedHistory[-num_steps:]
    else:
        if not hasattr(obj, 'history'):
            # if its a sensed component, the  history is abstracted in the comp attribute
            if hasattr(obj, 'comp') and hasattr(obj.comp, 'history'):
                return obj.comp.history[-num_steps:]
            
            # if its a sensed system, the history is abstracted in the system attribute
            elif hasattr(obj, 'system') and hasattr(obj.system, 'history'):
                return obj.system.history[-num_steps:]
        else:
            return obj.history[-num_steps:]


    # # if isinstance(obj, SensedComp) and sensed:
    # if sensed and hasattr(obj, 'sensedHistory'):
    #     return obj.sensedHistory[-num_steps:]
    # elif sensed and not hasattr(obj, 'sensedHistory'):
    #     print(type(obj), 'does not have sensedHistory attribute.')
    # elif not sensed and hasattr(obj, 'history'):
    #     return obj.history[-num_steps:]
    # else:
    #     print(type(obj), 'does not have history attribute.')
    #     # raise ValueError("get_history: Object does not have sensedHistory attribute.")


    # return obj.sensedHistory[-num_steps:] if sensed else obj.history[-num_steps:]

def SolveStructureFunction(objects:list, parallels: list[tuple], num_steps, sensed: bool = False) -> int:
    ''' calculate the structure function of either a system of sensed components or a ship of systems '''

    all_comps_history = np.array([get_history(obj, num_steps, sensed) for obj in objects], dtype=int)  # shape (n_comps, n_steps)
    
    # if parallels is None, all comps are in series
    if parallels is None: 
        Xi_temp = all_comps_history  # shape (n_comps, n_steps)
        phi_series = np.min(all_comps_history, axis=0)  # shape (n_steps,)
        return phi_series

    # determine the state of each parallel set first
    if parallels is not None: 
        for parallel_sets in parallels:

            # subtract 1 from each value to get the idx
            parallel_comps_idx = [i-1 for i in parallel_sets]

            # parallel_objs = [objects[i] for i in parallel_comps_idx]  # get the objects in the parallel set
            Xi_parallel_set = np.array([all_comps_history[i] for i in parallel_comps_idx])  # shape (n_parallel_comps, n_steps)
            phi_parallel_set = np.max(Xi_parallel_set, axis=0)  # shape (n_steps,)

        series_comp_idxs = []  # list to store the idx of series components
        objects_in_parallel = [i-1 for sublist in parallels for i in sublist]  # get all objects in parallel sets
        for i in range(len(objects)):
            if i not in objects_in_parallel:
                series_comp_idxs.append(i)
        if series_comp_idxs == []:  # if there are no series components
            return phi_parallel_set
        else:
            Xi_series_set = np.array([all_comps_history[i] for i in series_comp_idxs])  # shape (n_series_comps, n_steps)
            phi_series_set = np.min(Xi_series_set, axis=0)  # shape (n_steps,)

            # final consideration of all states in overall system state vector
            Xi_overall = np.vstack((phi_parallel_set, phi_series_set))
            phi_sys = np.min(Xi_overall, axis=0)            # shape (n_steps,)
            return phi_sys


def idx2letter(idx):
    """ Convert an index to a letter (1 -> A, 2 -> B, etc.) """
    if idx < 1:
        raise ValueError("Index must be greater than or equal to 1")
    return chr(idx + 64)  # ASCII value of 'A' is 65

def wrap_text_in_box(ax, text, box_size, xlims, ylims):
    """Wraps text to fit within a box of given size."""
    
    fontsize  = 8    
    wrapped_text = '\n'.join(textwrap.wrap(text, width=int(box_size * fontsize), break_long_words=False)) # 8 letters per box size

    return wrapped_text, fontsize

def generate_centered_list(center, num_values, min_spacing=1.0) -> list:
    """Evenly spaces values around a center point, with a minimum spacing."""
    if num_values <= 0:
        return []
    if num_values == 1:
        return [center]

    # Compute total span needed for minimum spacing
    total_span = (num_values - 1) * min_spacing
    start = center - total_span / 2
    end = center + total_span / 2

    values = np.linspace(start, end, num_values)
    return values.tolist()

def round_to_nearest_base(x, base):
    return base * round(x / base)

def set_x_ticks(ax, history_len, max_ticks=10):
    """
    Limit the number of x-axis ticks to clean, rounded intervals (multiples of 5 or 10).

    Parameters:
    - ax: matplotlib axis object
    - history_len: int, length of the data series being plotted
    - max_ticks: int, maximum number of ticks to display
    """
    if history_len <= 1:
        ax.set_xticks([0])
        return

    raw_step = history_len / (max_ticks)

    # Round to nearest clean interval
    step = round_to_nearest_base(raw_step, 10) if raw_step >= 10 else round_to_nearest_base(raw_step, 5)
    step = max(1, step)

    ticks = np.arange(0, history_len, step)

    # Only append the last point if it's not too close to the last tick
    if (history_len - 1) - ticks[-1] >= step / 2:
        ticks = np.append(ticks, history_len - 1)

    ax.set_xticks(ticks)


def create_multi_simulation_table(headers, rows):
    """ Create a table summarizing the results of multiple simulations """
    return tabulate.tabulate(rows, headers=headers, tablefmt="grid")



def compress_folder_to_zip(source_folder, output_zip_name):
    """
    Compresses a specified folder into a zip archive.

    Args:
        source_folder (str): The path to the folder to be compressed.
        output_zip_name (str): The desired name for the output zip file
                                (without the .zip extension).
    """
    try:
        # Get the absolute path of the source folder
        source_folder_abs = os.path.abspath(source_folder)
        
        # Create the zip archive
        shutil.make_archive(output_zip_name, 'zip', source_folder_abs)
        print(f"Folder '{source_folder}' successfully compressed to '{output_zip_name}.zip'")
    except Exception as e:
        print(f"Error compressing folder: {e}")

    # remove the original folder after compression
    try:
        shutil.rmtree(source_folder)
        print(f"Original folder '{source_folder}' has been removed.")
    except Exception as e:
        print(f"Error removing original folder: {e}")