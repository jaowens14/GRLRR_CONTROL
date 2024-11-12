import subprocess
import re
import numpy as np
import matplotlib.pyplot as plt

# Use Popen to get a process handle
process = subprocess.Popen(
    ["./rplidar_sdk/output/Linux/Release/ultra_simple", "--channel", "--serial", "/dev/ttyUSB0", "460800"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True
)

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.set_ylim(0, .25)  # Set a reasonable range for distances
ax.set_theta_offset(np.pi / 2)  # Set theta = 0 at the top

# Lists to store the angle (theta) and distance (Dist) values
ds = []
ts = []
i = 0

try:
    while True:
        # Read a line of data from the process's stdout
        line = process.stdout.readline()

        # If no line is received, continue (i.e., wait for the next line)
        if not line:
            continue

        # Decode and print the line for debugging purposes
        line = line.strip()  # Strip any extra whitespace/newlines
        print(f"Raw line: {line}")  # You can remove this after debugging

        if 'theta' in line:
            # Try to extract the relevant data (theta, Dist, and Q)
            try:
                theta = float(re.search(r'theta:\s*([\d.]+)', line).group(1))
                dist = float(re.search(r'Dist:\s*([\d.]+)', line).group(1))
                #q = float(re.search(r'Q:\s*([\d.]+)', line).group(1))  # If you need Q value
                ts.append(np.radians(theta))
                
                ds.append(dist/1000.0)

            except AttributeError:
                pass  # In case the regular expression fails (ignores this line)

        # Every 500 readings, update the plot
        if 'S' in line:
            ax.clear()  # Clear previous plot
            ax.set_ylim(0, 0.25)  # Reset the distance limit
            ax.set_theta_offset(np.pi / 2)  # Set theta = 0 at the top

            ax.scatter(ts, ds)  # Plot the points
            ax.set_title("Lidar Data (Polar Plot)")

            # Display the plot with non-blocking update
            plt.pause(0.1)  # Pause briefly to allow the plot to update

            # Reset the data after plotting
            ts.clear()
            ds.clear()
            i = 0  # Reset the counter

except KeyboardInterrupt:
    print("Process interrupted by user.")

finally:
    process.kill()  # Ensure the process is killed when the program ends
    print("Process terminated.")
