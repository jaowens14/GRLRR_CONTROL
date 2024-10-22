import asyncio
from simple_pid import PID
from logger import Logger
from queues import Queues

# this is designed to map angles and offsets to velocities

# input angles from say -5 deg to 5 deg.
# input offsets from -0.04% to 0.04%

# the output of the pid should be 0 if deg    is 0
# the output of the pid should be 0 if offset is 0

# the output should be a faster motor on the left if the angle is negative
# the output should be a faster motor on the right if the angle is positive 

# the output should be a faster motor on the left if the offset is negative
# the output should be a faster motor on the right if the offset is positive

# the output should be gotten from the offset PID until it is with a specific range



class Steering():
    def __init__(self, logger:Logger, queues:Queues):
        self.logger = logger
        self.mode = ''
        self.mcu_writes = queues.mcu_writes
        self.angles = queues.angles
        self.offsets = queues.offsets
        self.steering = True
        self.p = -0.1
        self.i = 0.0
        self.d = 0.0
        self.set_point = 0.0
        self.process_speed = 0.020
        
        # angle pid
        self.angle_pid = PID(Kp=self.p, Ki=self.i, Kd=self.d, setpoint=self.set_point)
        self.angle_pid.sample_time = 0.1 # seconds
        self.angle_pid.output_limits = (-0.05, 0.05)    # Output value will be between -0.01 and 0.01 m/s

        # offset pid
        #self.offset_pid = PID(Kp=self.p*5.0, Ki=self.i, Kd=self.d, setpoint=self.set_point)
        #self.offset_pid.sample_time = 0.1
        #self.offset_pid.output_limits = (-0.05, 0.05)
        #self.offset_deadband = (-0.03, 0.03)

    async def run(self):
        try:
            while True:
                current_angle = await self.angles.get()
                current_offset = await self.offsets.get()
                # if the robot is within the tolerance then just correct for angle
                #if min(self.offset_deadband) < current_offset <= max(self.offset_deadband):
                self.angle_pid.setpoint = 0.0
                u = self.angle_pid(current_offset)
                # if the robot is not within the side to side tolerance then move the angle setpoint to 'steer' in the direction needed
                #
                #else:
                #    self.angle_pid.setpoint = self.angle_pid.setpoint - current_offset
                #    u = self.angle_pid(current_angle)

                ## if the offset is within the dead band, switch to use the angle pid
                #if min(self.offset_deadband) < current_offset <= max(self.offset_deadband):
                #    u = self.angle_pid(current_offset)
                #    self.logger.log.info("using angle pid")
                #else:
                ## else move the set point of the angle pid
                #    #u = self.offset_pid(current_angle)
                #    self.logger.log.info("using offset pid")

                left_speed =  round(self.process_speed - u, 4)
                right_speed = round(self.process_speed + u, 4)
                self.logger.log.info('angle: '+str(current_angle)+
                                     ' offset: '+str(current_offset)+
                                     ' left: '+str(left_speed)+
                                     ' right: '+str(right_speed)+
                                     ' u: '+str(u))

                # m1 is the left side right now, m4 is the right side
                cmd = {"msgtyp":"set", "motorSpeed0": -1.0 * float(left_speed), 
                                       "motorSpeed1": -1.0 * float(left_speed),
                                       "motorSpeed2": float(right_speed),
                                       "motorSpeed3": float(right_speed)}
                self.logger.log.debug(cmd)
                await self.mcu_writes.put(cmd)

        except Exception as e:
            self.logger.log.info(e.__class__.__name__)
        except asyncio.CancelledError:
            self.logger.log.info("steering cancelled")
            self.mcu_writes.put_nowait({"msgtyp":"set", "motorSpeed0": -1.0 * float(0.0), 
                                   "motorSpeed1": -1.0 * float(0.0),
                                   "motorSpeed2": float(0.0),
                                   "motorSpeed3": float(0.0)})
