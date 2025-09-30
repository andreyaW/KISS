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
def get_history(obj, sensed: bool = False) -> np.ndarray:
    return obj.sensedHistory if sensed else obj.history

def SolveStructureFunction(objects: list, parallels: list[tuple] = None, num_steps: int = 0, sensed: bool = False) -> np.ndarray:
    """
    Calculate the structure function of a system of components with series and parallel configurations.
    Returns a NumPy array of system states over the last `num_steps` timesteps.

    Parameters
    ----------
    objects : list
        List of Component-like objects with `.history` and optionally `.sensedHistory`.
    parallels : list of tuple
        Each tuple contains 1-based indices of components in parallel.
    num_steps : int
        Number of most recent timesteps to include (0 means use full history).
    sensed : bool
        If True, use .sensedHistory instead of .history.

    Returns
    -------
    np.ndarray
        Array of system states over time (shape: [num_timesteps]).
    """

    # Slice only the last `num_steps`
    def sliced_history(obj):
            return get_history(obj, sensed)[-num_steps:]

    parallel_results = []

    # Handle parallel sets
    if parallels is not None:
        for p_set in parallels:
            idx = [i - 1 for i in p_set]  # convert to 0-based
            parallel_histories = np.vstack([sliced_history(objects[i]) for i in idx])
            # system works if any component in the parallel set works
            parallel_results.append(np.max(parallel_histories, axis=0))  # shape: (num_steps,)

    # Series components not in any parallel set
    if parallels is not None:
        parallel_indices = [i - 1 for sub in parallels for i in sub]
        series_indices = [i for i in range(len(objects)) if i not in parallel_indices]
    else:
        series_indices = list(range(len(objects)))

    if series_indices:
        series_histories = np.vstack([sliced_history(objects[i]) for i in series_indices])
        series_result = np.min(series_histories, axis=0)
        parallel_results.append(series_result)

    # Combine parallel sets and series components: system fails if any subset fails
    if parallel_results:
        phi = np.min(np.vstack(parallel_results), axis=0)
    else:
        # No components? Return all zeros
        phi = np.zeros(num_steps, dtype=int)

    return phi  # shape: (num_steps,)


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