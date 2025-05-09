import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from utils.helperFunctions import wrap_text_in_box, generate_centered_list

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
        
        self.comp_locations = {}  # dictionary to store the locations of the components in the system

# ---- functions to draw the system on the axis ----
    def drawBox(self, x:float = 0 ,y:float = 0, box_size = 1) -> None:
        """draws a square box at the given coordinates"""

        # grab the current axis if not provided
        ax = self.ax

        # draw a box at the given coordinates
        plt.gca().add_patch(Rectangle((x, y), box_size, box_size, fill=None, edgecolor='black', lw=2))

        # adjust the axes to accommodate the new box
        self.drawing_width = self.drawing_width + box_size + 1
        self.drawing_height = self.drawing_height + box_size
        self.adjustAxes(x,y, box_size)



    def drawComp(self, comp, x, y, box_size = 2) -> None:
        """draws a component at the given coordinates"""
        
        # draw a box at the given coordinates
        self.drawBox(x, y, box_size)
    
        # add comp name to the box 
        text = comp.name
        wrapped_text, fontsize= wrap_text_in_box(self.ax, text, box_size, self.xlims, self.ylims)
        self.ax.text(x + (box_size / 2), 
                        (y + 2*box_size / 3), 
                        wrapped_text, 
                        ha='center', va='center', fontsize=fontsize, color='black')

        # add comp true state to the box
        if comp.state == max(list(comp.comp.states)):
            state_color = "green"
        elif comp.state != 0: 
            state_color = "blue"
        if comp.state == 0:
            state_color = "red"
        comp_state = comp.comp.states[comp.state]  # get the state of the component
        text = f"Truth: {comp_state}"
        wrapped_text, fontsize= wrap_text_in_box(self.ax, text, box_size, self.xlims, self.ylims)
        self.ax.text(x + (box_size / 2), 
                        (y + box_size / 3), 
                        wrapped_text, 
                        ha='center', va='center', fontsize=fontsize, color=state_color)

        # add comp sensed state to the box
        if comp.sensedState == max(list(comp.comp.states)):
            sensed_state_color = "green"
        elif comp.sensedState != 0:
            sensed_state_color = "blue"
        if comp.sensedState == 0:
            sensed_state_color = "red"
        
        comp_sensed_state = comp.comp.states[comp.sensedState]  # get the state of the component
        text = f"Sensed: {comp_sensed_state}"
        wrapped_text, fontsize= wrap_text_in_box(self.ax, text, box_size, self.xlims, self.ylims)
        self.ax.text(x + (box_size / 2),
                    (y + box_size / 3) - 0.25, 
                    wrapped_text, 
                    ha='center', va='center', fontsize=fontsize, color=sensed_state_color)
                     


    def defineLocations(self, system, compsize = 2, spacing=1) -> dict:
        """ defines a x,y tuple for each component in the system"""
        
        # define the locations of the components in the system
        locations = {}
        x = 0           # initial x coordinate of the first component
        for i, comp in enumerate(system.comps):
            
            # if there are parallels, their locations are defined more specifically
            if system.parallels != None: 
                
                # go through each parallel group and define their locations
                for j in range(len(system.parallels)):
                    comp_idx = i+1
                    if comp_idx in system.parallels[j]:
                        # if the component is in a parallel group, set the x coordinate to be the same as the first component in the group
                        # print(f"{comp.name} is in parallel group {j+1}")
                        
                        # define the x coordinate of the first component in the group
                        if comp_idx == system.parallels[j][0]:
                            pass    # no change, the x coordinate is already set at the end of the for loop
                        
                        # defining the x coordinate of the remaining components in the group to match the first
                        if comp_idx != system.parallels[j][0]:
                            x = locations[system.comps[system.parallels[j][0]-1]][0]

                        # define the y coordinates of the set to center along y = 0 
                        n_pars = len(system.parallels[j])  # number of components in the parallel group
                        y_s = generate_centered_list(0, n_pars, (compsize/2+spacing/2))  # create a list of y coordinates for the parallel group
                        y_s.sort(reverse=True) # reverse the list to have the first component at the top
                        y = y_s[system.parallels[j].index(comp_idx)] * compsize # get the y coordinate of the current component in the parallel group    
                            
                        break

                    else: 
                        # if index is not in any parallel groups, leave x coordinate alone and set y to 0
                        y = 0
            
            # if there are no parallels, all comps have the y coordinate set to 0
            elif system.parallels == None:
                y = 0            
            
            # add the component to the locations dictionary
            locations[comp] = (x, y)
            
            # update x for the next component
            x_s = [loc[0] for loc in locations.values()]    # get the x coordinates of all components in the system
            x_max = max(x_s) if x_s else x                  # get the maximum x coordinate of all components in the system
            x = x_max+ compsize + spacing

        self.comp_locations = locations  # store the locations of the components in the system
        # return locations
    

    def drawConnections(self, system, compsize, spacing) -> None:
        """draws a connection between two boxes"""
        
        # define the connection points based on the locations of the components
        for i, comp in enumerate(self.comp_locations.keys()):
            
            if system.parallels != None:

                # draw connections between components in parallel groups
                for j in range(len(system.parallels)):
                    comp_idx = i+1
                    if comp_idx in system.parallels[j]:
                        print("need to draw connection between parallel components")
                        pass
                    else:
                        # if index is not in any parallel groups, draw a straight line to the next component
                        self.drawSeriesConnections(system, comp, compsize, i)

            else:
                # draw connections between components in series
                self.drawSeriesConnections(system, comp, compsize, i)
                

    def drawSeriesConnections(self, system, comp, compsize, i) -> None:
        # get the x,y coordinates of the current component
        if i == len(system.comps) - 1:
            pass
        else:
            # if the current component is not the last one, draw a line to the next component
            x1, y1 = self.comp_locations[comp]
            x2, y2 = self.comp_locations[system.comps[i+1]]
            x1 = x1 + compsize
            y1, y2 = y1 + compsize/2, y2 + compsize/2
            plt.plot([x1, x2], [y1, y2], color='black', lw=2, linestyle='--')

    
    def displayDiagram(self): 
        """final touches then displays the diagram"""
        
        # remove the axes for better visualization
        self.ax.axis('off')
        
        # show the plot
        plt.show()


# ---- functions to adjust the display of the axis----
    def adjustAxes(self, x, y, box_size) -> None:
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
        
        # grab current figure and set the width to the drawing width
        fig = plt.gcf()
        fig.set_figwidth(self.drawing_width)












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