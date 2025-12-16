"""Cycle visualization module."""
import numpy as np
import matplotlib.pyplot as plt

class Cycle:
    def __init__(self,
                num_parts: int = 4,
                labels : list[str] = ('1','2','3','4')):
        self.num_parts = num_parts
        self.labels = labels

    def show(self,
                title : str = 'Cycle of parts and labels'):
        # Show parts (angles) and labels in circle

        # Convert parts to angles
        angles = np.linspace(0, 2 * np.pi, self.num_parts, endpoint=False)

        # Create a figure and axis
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

        # Plot the labels
        for angle, label in zip(angles, self.labels):
            ax.plot(angle, 1, 'o', markersize=10)
            ax.text(angle, 1.1, str(label), ha='center', va='center')

        # Set the title
        ax.set_title(title)
        # Show the plot
        plt.show()
