import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Create a figure and axis for the animation
fig, ax = plt.subplots()
ax.set_aspect('equal')  # Set aspect ratio to ensure a circular shape

# Initialize the circle at the center
circle = plt.Circle((0, 0), 1, fill=False, color='b')
ax.add_artist(circle)

# Initialize the encoder data (angle in radians)
encoder_data = np.linspace(0, 2 * np.pi, 360)  # 360 data points for a full circle

# Initialize an empty scatter plot for the current point
point, = plt.plot([], [], 'ro')  # Red point for the current position

# Function to initialize the animation
def init():
    point.set_data([], [])
    return point,

# Function to update the position of the current point
def update(frame):
    # Get the current encoder value (angle in radians)
    angle = encoder_data[frame]

    # Calculate the new position of the point on the circle
    x = np.cos(angle)
    y = np.sin(angle)

    # Update the position of the point
    point.set_data(x, y)
    
    return point,

# Create an animation
animation = FuncAnimation(fig, update, frames=len(encoder_data), init_func=init, blit=True, interval=100)

# Set axis limits to fit the circle
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)

# Display the animation
plt.title('Circle Animation: Plotting Points on Circle')
plt.gca().set_aspect('equal', adjustable='box')
plt.grid(True)
plt.show()
