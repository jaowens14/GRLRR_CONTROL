import subprocess
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib 
import signal
import traceback
from scipy.signal import savgol_filter
np.set_printoptions(suppress=True)
plt.ion()


def get_xs(scan):
    return (np.cos(np.radians(scan[:,0])) * scan[:,1]).reshape(-1,1)

def get_ys(scan):
    return (np.sin(np.radians(scan[:,0])) * scan[:,1]).reshape(-1,1)


def get_abs_diffs(scan):
    return np.sqrt(np.square(np.diff(scan[:, 1], append=np.zeros(1)).reshape(-1,1))) # diffs in distance



def show_me_the_data(scan_array):

    x = np.cos(np.radians(scan_array[:, 0]))*scan_array[:,1] # 90 is added to rotate the chart
    y = np.sin(np.radians(scan_array[:, 0]))*scan_array[:,1]


    ax1.set_xlim(-200.0, 200.0)  # Set a reasonable range for distances
    ax1.set_ylim(-200.0, 200.0)  # Set a reasonable range for distances
    ax1.scatter(0,0)

    for angle in [0.0, 30.0, 330.0]:
        roi_x = np.cos(np.radians(angle)) * 300.0 # 90 is added to rotate the chart
        roi_y = np.sin(np.radians(angle)) * 300.0
        print(roi_x)
        ax1.plot([0, roi_x], [0, roi_y], '--', linewidth=2)

    ax1.scatter(x,y, marker='x')

    plt.pause(0.1)



def grab_scan():
    scan = []
    while True:
        line = process.stdout.readline()
        if 'sync' in line:
            sync = int(re.search(r'sync:\s*([\d.]+)', line).group(1))
            theta = float(re.search(r'theta:\s*([\d.]+)', line).group(1))
            dist = float(re.search(r'Dist:\s*([\d.]+)', line).group(1))
            q = float(re.search(r'Q:\s*([\d.]+)', line).group(1))

            if sync == 1:
                return scan
            else:
                scan.append([theta, dist, q])

def scan_to_array(scan):
    return np.array(scan)

def smooth_scan(scan):
    kernel_size = 30
    kernel = np.ones(kernel_size) / kernel_size
    scan[:,0] = np.convolve(scan[:,0], kernel, mode='same')
    scan[:,1] = np.convolve(scan[:,1], kernel, mode='same')
    return scan

def clear_out_zero_distances(scan):
    return scan[scan[:,1] > 0.0]

def extract_left_and_right_sides(scan):
    # col 0 is the degs
    left = scan[scan[:,0] < 30.0]
    right = scan[scan[:,0] > 330.0]
    return left, right

def find_edges_of_web(scan):
    '''instead of using an index we will 
    get the deg value next to the largest 
    discontinuity in order to keep the data aligned'''
    scan = clear_out_zero_distances(scan)

    #scan = smooth_scan(scan)

    xs = get_xs(scan)
    ys = get_ys(scan)
    
    diffs = get_abs_diffs(scan)

    scan = np.column_stack([scan, diffs, xs, ys])

    left, right = extract_left_and_right_sides(scan)
    
    right_edge = right[np.argmax(right[:, 3])+1] # this plus 1 is added due to how the differences are calculated
    right_x = right_edge[-2]
    right_y = right_edge[-1]


    left_edge = left[np.argmax(left[:, 3])]
    left_x = left_edge[-2]
    left_y = left_edge[-1]


    ax1.scatter(right_x,right_y)
    ax1.scatter(left_x, left_y)

    ax1.plot([0, right_x], [0, right_y], '--', linewidth=2)
    ax1.plot([0, left_x], [0, left_y], '--', linewidth=2)
    percent = (left_y+right_y)/left_y-right_y - 50.0
    print(percent)
    ax1.text(-150, -150, str(percent))
    return percent




matplotlib.use('TkAgg')

# Use Popen to get a process handle
process = subprocess.Popen(
    ["./rplidar_sdk/output/Linux/Release/ultra_simple", "--channel", "--serial", "/dev/ttyUSB0", "460800"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True
)

fig1 = plt.figure(figsize=(10, 10))  # Increase figure size
ax1 = fig1.add_subplot(111)

while True:
    try:
        scan = grab_scan()
        if scan:
            scan_array = scan_to_array(scan)
            
            find_edges_of_web(scan_array)

            show_me_the_data(scan_array)
            input()            
            ax1.clear()

        #l, r = extract_left_and_right_sides(scan_array)
    except Exception as e:
        traceback.print_exc()
        process.send_signal(signal.SIGINT)
        process.wait()
        exit()
    except KeyboardInterrupt:
        print("EXITED")
        process.send_signal(signal.SIGINT)
        process.wait()
        exit()

try:
    while True:
        # Read a line of data from the process's stdout
        line = process.stdout.readline()
        line = line.strip()  

        if 'theta' in line:
            # Try to extract the relevant data (theta, Dist, and Q)
            try:
                
                sync = float(re.search(r'sync:\s*([\d.]+)', line).group(1))

                theta = float(re.search(r'theta:\s*([\d.]+)', line).group(1))
                dist = float(re.search(r'Dist:\s*([\d.]+)', line).group(1))
                q = float(re.search(r'Q:\s*([\d.]+)', line).group(1))
                # it is known that theta = 0 is right in the front middle of the robot
                # therefore theta 0 to 20 is the left side of the scan
                # and 340 to 360 is the right side of the scan
                x = (np.cos(np.radians(theta))*dist) # 90 is added to rotate the chart
                y = (np.sin(np.radians(theta))*dist)
                

                ts.append(np.radians(theta))
                ds.append(dist/1000.0)
                if theta < 30.0:
                    leftX.append(x)
                    leftY.append(y)
                if theta > 330.0:
                    rightX.append(x)
                    rightY.append(y)

            except AttributeError:
                pass  # In case the regular expression fails (ignores this line)

        if 'S ' in line:
            
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
            #input()

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
