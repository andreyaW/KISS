import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

class systemDiagram():
    """A class to draw a system of sensed components as boxes on a matplotlib axis.
    
    Attributes:
        ax (matplotlib.axes.Axes): The axes on which to draw the boxes.
    """
    
    def __init__(self, ax = None) -> None:
        """Initializes the drawSystem class.
        
        Args:
            ax (matplotlib.axes.Axes, optional): The axes on which to draw the boxes. Defaults to None.
        """
        
        if ax is None:
            # create a new figure and axis if no axis is provided
            fig, self.ax = plt.subplots()
        else:
            self.ax = ax

        # parameters to track to the size of the drawing area
        self.xlims = self.ax.get_xlim()
        self.ylims = self.ax.get_ylim()
        self.drawing_width = 0              # no items drawn yet 
        self.drawing_height = 0             # no items drawn yet


# ---- functions to draw the system on the axis ----
def draw_box(self, x:float = 0 ,y:float = 0) -> None:

    # grab the current axis if not provided
    ax = self.ax

    # draw a box at the given coordinates
    plt.gca().add_patch(Rectangle((x, y), 1, 1, fill=None, edgecolor='black', lw=2))


# ---- functions to adjust the display of the axis----


























# def adjust_axes(ax, x, y) -> None:
#     """adjusts the axes of the given axis to make sure it accommadates an added box
    
#     Args:
#         ax (matplotlib.axes.Axes): The axes to adjust.
#         x (tuple): The x-coordinate of the added items bottom-left corner.
#         y (tuple): The y-coordinate of the added items bottom-left corner.
#     """
    
#     # get the current limits of the axes
#     xlim = list(ax.get_xlim())
#     ylim = list(ax.get_ylim())
    
#     print(xlim,'/n',ylim)
#     print(x,y)
    
#     # calculate the new limits based on the added box
#     # (assuming the box is 1x1 in size and you want a margin of 1 unit)
#     xlim[0] = min(xlim[0], x-1)
#     xlim[1] = max(xlim[1], x+2)

#     # set the new limits for the axes
#     ax.set_xlim(xlim)
#     ax.set_ylim(ylim)



# def draw_box(ax = None , x:float = 0 ,y:float = 0) -> None:
#     """draws a box at the given coordinates
    
#     Args:
#         ax (matplotlib.axes.Axes): The axes on which to draw the box.
#         x (float): The x-coordinate of the box's bottom-left corner.
#         y (float): The y-coordinate of the box's bottom-left corner.
#     """
    
#     if ax is None:
#         # create a new figure and axis if no axis is provided
#         fig, ax = plt.subplots()
    
#     # draw a box at the given coordinates
#     plt.gca().add_patch(Rectangle((x, y), 1, 1, fill=None, edgecolor='black', lw=2))
#     adjust_axes(ax,x,y)
    
#     # display the drawing and return the current axis
#     plt.show()
#     return ax