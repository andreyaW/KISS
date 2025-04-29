import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from helperFunctions import wrap_text_in_box

class SystemDiagram():
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
        self.xlims = list(self.ax.get_xlim())
        self.ylims = list(self.ax.get_ylim())
        self.drawing_width = 0              # no items drawn yet, all drawings start at 0,0
        self.drawing_height = 0             # no items drawn yet, all drawings start at 0,0
        


# ---- functions to draw the system on the axis ----
    def draw_box(self, x:float = 0 ,y:float = 0, box_size = 1) -> None:
        """draws a square box at the given coordinates"""

        # grab the current axis if not provided
        ax = self.ax

        # draw a box at the given coordinates
        plt.gca().add_patch(Rectangle((x, y), box_size, box_size, fill=None, edgecolor='black', lw=2))

        # adjust the axes to accommodate the new box
        self.drawing_width = self.drawing_width + box_size
        self.drawing_height = self.drawing_height + box_size
        self.adjust_axes(x,y, box_size)



    def draw_comp(self, comp, x, y, box_size = 2) -> None:
        """draws a component at the given coordinates"""
        
        # draw a box at the given coordinates
        self.draw_box(x, y, box_size)
    
        # add comp name to the box 
        text = comp.name
        wrapped_text = wrap_text_in_box(self.ax, text, box_size, fontsize=8)
        self.ax.text(x + (box_size / 2), 
                        (y + box_size / 2), 
                        wrapped_text, 
                        ha='center', va='center', fontsize=8, color='black')

        # add comp state to the box
        if comp.state == max(list(comp.comp.states)):
            state_color = "green"
        elif comp.state != 0: 
            state_color = "blue"
        if comp.state == 0:
            state_color = "red"
        comp_state = comp.comp.states[comp.state]  # get the state of the component
        text = f"State: {comp_state}"
        wrapped_text = wrap_text_in_box(self.ax, text, box_size, fontsize=8)
        self.ax.text(x + (box_size / 2), 
                        (y + box_size / 2) - 0.25, 
                        wrapped_text, 
                        ha='center', va='center', fontsize=8, color=state_color)




# ---- functions to adjust the display of the axis----
    def adjust_axes(self, x, y, box_size) -> None:
        """adjusts the axes of the given axis to make sure it accommodates an added box
        
        Args:
            ax (matplotlib.axes.Axes): The axes to adjust.
            x (tuple): The x-coordinate of the added items bottom-left corner.
            y (tuple): The y-coordinate of the added items bottom-left corner.
        """

        lims_width = self.xlims[1] - self.xlims[0]
        lims_height = self.ylims[1] - self.ylims[0]    
        spacing_unit = 1

        # calculate the new limits based on the added box's x,y coordinates
        # (assuming the box_size is given and you want a margin of 1 unit)
        if lims_width < self.drawing_width + 2:
           
            if self.xlims[0] > x - spacing_unit:
                self.xlims[0] = x - spacing_unit

            if self.xlims[1] < x + box_size + spacing_unit:
                self.xlims[1] = x + box_size + spacing_unit

        if lims_height < self.drawing_height + 2:
            if self.ylims[0] > y - spacing_unit:
                self.ylims[0] = y - spacing_unit

            if self.ylims[1] < y + box_size + spacing_unit:
                self.ylims[1] = y + box_size + spacing_unit            

        # set the new limits for the axes
        self.ax.set_xlim(self.xlims)
        self.ax.set_ylim(self.ylims)













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