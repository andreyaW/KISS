import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def adjust_axes(ax, x, y) -> None:
    """adjusts the axes of the given axis to make sure it accommadates an added box
    
    Args:
        ax (matplotlib.axes.Axes): The axes to adjust.
        x (tuple): The x-coordinate of the added items bottom-left corner.
        y (tuple): The y-coordinate of the added items bottom-left corner.
    """
    
    # get the current limits of the axes
    xlim = list(ax.get_xlim())
    ylim = list(ax.get_ylim())
    
    print(xlim,'/n',ylim)
    print(x,y)
    
    # calculate the new limits based on the added box
    xlim[0] = min(xlim[0], x-1)
    xlim[1] = max(xlim[1], x + 2)  # assuming the box width is 1
    ylim[0] = min(ylim[0], y -1)
    ylim[1] = max(ylim[1], y + 2)  # assuming the box height is 1

    # set the new limits for the axes
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)



def draw_box(ax = None , x:float = 0 ,y:float = 0) -> None:
    """draws a box at the given coordinates
    
    Args:
        ax (matplotlib.axes.Axes): The axes on which to draw the box.
        x (float): The x-coordinate of the box's bottom-left corner.
        y (float): The y-coordinate of the box's bottom-left corner.
    """
    
    if ax is None:
        # create a new figure and axis if no axis is provided
        fig, ax = plt.subplots()
    
    # draw a box at the given coordinates
    plt.gca().add_patch(Rectangle((x, y), 1, 1, fill=None, edgecolor='black', lw=2))
    adjust_axes(ax,x,y)
    
    # display the drawing and return the current axis
    plt.show()
    return ax