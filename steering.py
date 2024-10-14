import asyncio
from simple_pid import PID

# this is designed to map angles and offsets to velocities

# input angles from say -5 deg to 5 deg.
# input offsets from -20% to 20%

# the output of the pid should be 0 if deg    is 0
# the output of the pid should be 0 if offset is 0

# the output should be a faster motor on the left if the angle is negative
# the output should be a faster motor on the right if the angle is positive 

# the output should be a faster motor on the left if the offset is negative
# the output should be a faster motor on the right if the offset is positive

# the output should be gotten from the offset PID until it is with a specific range

class Steering():
    def __init__(self, qs):
        self.mcu_write = qs.mcu_write

        self.p = 0.001
        self.i = 0.0
        self.d = 0.0
        self.set_point = 0.0
        self.process_speed = 0.01

        self.angle_pid = PID(Kp=self.p, Ki=self.i, Kd=self.d, setpoint=self.set_point)
        self.angle_pid.sample_time = 0.1 # seconds
        self.angle_pid.output_limits = (-0.05, 0.05)    # Output value will be between -0.01 and 0.01 m/s

        self.angle_pid = PID(Kp=self.p, Ki=self.i, Kd=self.d, setpoint=self.set_point)
        self.offset_pid.sample_time = 0.1
        self.offset_pid.output_limits = (-0.05, 0.05)
        self.offset_deadband = (-10.0, 10.0)


    async def run():
        while True:
            if steering:
                current_angle = await angle_queue.get()
                current_offset = await offset_queue.get()
                # if the offset is within the dead band, switch to use the angle pid
                if min(offset_deadband) < current_offset <= max(offset_deadband):
                    u = angle_pid(current_offset)
                    grlrr_log.debug("using angle pid")
                else:
                    u = offset_pid(current_angle)

                #grlrr_log.info("angle: "+str(current_angle))
                #grlrr_log.info("offset: "+str(current_offset))
                ##grlrr_log.info("u = pid(angle) + pid(offset)")
                #grlrr_log.info("steering inputs: ")
                #grlrr_log.info("angle u: "+str(angle_pid(current_angle)))
                #grlrr_log.info("offset u: "+str(offset_pid(current_offset)))

                left_speed = round(process_speed - u/2, 4)
                right_speed = round(process_speed + u/2, 4)
                # m1 is the left side right now, m4 is the right side
                cmd = {"msgtyp":"set", "motorSpeed0": -1.0 * float(left_speed), 
                                       "motorSpeed1": -1.0 * float(process_speed),
                                       "motorSpeed2": float(process_speed),
                                       "motorSpeed3": float(right_speed)}




                grlrr_log.debug(cmd)
                #await command_queue.put(cmd)
            else:
                await asyncio.sleep(0)