import subprocess
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib 


def find_edge_of_web(side):
    print(side)
    input()
matplotlib.use('TkAgg')

# Use Popen to get a process handle
process = subprocess.Popen(
    ["./rplidar_sdk/output/Linux/Release/ultra_simple", "--channel", "--serial", "/dev/ttyUSB0", "460800"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True
)

fig = plt.figure(figsize=(10, 10))  # Increase figure size
ax = fig.add_subplot(111, projection='polar')
ax.set_rlim(0.0, .25)  # Set a reasonable range for distances
ax.set_theta_offset(np.pi / 2)  # Set theta = 0 at the top

fig1 = plt.figure(figsize=(10, 10))  # Increase figure size
ax1 = fig1.add_subplot(111)
plt.ion()
# Lists to store the angle (theta) and distance (Dist) values
ds = []
ts = []
xs = []
ys = []

leftX = []
leftY = []
rightX = []
rightY = []

temp = []
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
                # it is known that theta = 0 is right in the front middle of the robot
                # therefore theta 0 to 20 is the left side of the scan
                # and 340 to 360 is the right side of the scan
                x = (np.cos(np.radians(theta+90.0))*dist) # 90 is added to rotate the chart
                y = (np.sin(np.radians(theta+90.0))*dist)

                ts.append(np.radians(theta))
                ds.append(dist/1000.0)
                if theta < 20:
                    leftX.append(x)
                    leftY.append(y)
                if theta > 340.0:
                    rightX.append(x)
                    rightY.append(y)


                

            except AttributeError:
                pass  # In case the regular expression fails (ignores this line)

        # Every 500 readings, update the plot
        if 'S' in line:
            
            #with open('distances.csv', 'a') as f:
            #    f.write('sample '+ '\n')
            #    for item in ds:
            #        f.write(str(item) + '\n')
            if len(rightY) > 0:
                right_side = np.hstack([np.array(rightX).reshape(-1,1), np.array(rightY).reshape(-1,1)])
                find_edge_of_web(right_side)
            ax1.clear()
            ax1.set_xlim(-200.0, 200.0)  # Set a reasonable range for distances
            ax1.set_ylim(-200.0, 200.0)  # Set a reasonable range for distances

            ax1.scatter(0,0)
            ax1.scatter(leftX, leftY)
            ax1.scatter(rightX, rightY)
            print(len(rightX))
            print(len(leftX))
            ax.clear()  # Clear previous plot
            ax.set_rlim(0.0, .25)  # Set a reasonable range for distances
            ax.set_theta_offset(np.pi / 2)  # Set theta = 0 at the top

            ax.scatter(ts, ds)  # Plot the points
            ax.set_title("Lidar Data (Polar Plot)")

            # Display the plot with non-blocking update
            plt.pause(0.1)  # Pause briefly to allow the plot to update
            #plt.show()
            # Reset the data after plotting
            input()

            leftX.clear()
            leftY.clear()
            rightX.clear()
            rightY.clear()
            ts.clear()
            ds.clear()
            xs.clear()
            ys.clear()

except KeyboardInterrupt:
    print("Process interrupted by user.")

finally:
    process.kill()  # Ensure the process is killed when the program ends
    print("Process terminated.")
