import asyncio
from queues import angle_queue, command_queue
from simple_pid import PID
from logger import grlrr_log

# this is designed to map angles to velocities
# input angles from say -5 deg to 5 deg.
# the output of the pid should be 0 if deg is 0
# the output should be a faster motor on the left if the angle is negative
# the output should be a faster motor on the right if the angle is positive 
process_speed = 0.01
pid = PID(0.001, 0.0, 0.0, setpoint=0)

pid.sample_time = 0.1 # seconds

pid.output_limits = (-0.05, 0.05)    # Output value will be between -0.01 and 0.01 m/s

steering = True

async def run_steering():
    while True:
        if steering:
            current_angle = await angle_queue.get()

            # get control input u from the PID
            u = pid(current_angle)

            #
            # print("left motor: ", round(process_speed - u/2, 4), "right motor: ", )

            left_speed = round(process_speed - u/2, 4)
            right_speed = round(process_speed + u/2, 4)
            # m1 is the left side right now, m4 is the right side
            cmd = {"msgtyp":"set", "motorSpeed0": -1.0 * float(left_speed), 
                                   "motorSpeed1": -1.0 * float(process_speed),
                                   "motorSpeed2": float(process_speed),
                                   "motorSpeed3": float(right_speed)}
            


            
            grlrr_log.info(cmd)
            #await command_queue.put(cmd)
        else:
            await asyncio.sleep(0)