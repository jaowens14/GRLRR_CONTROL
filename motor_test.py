import asyncio
from logger import Logger
from queues import Queues

# This script is created to test each motor individually to ensure proper function.

class MotorTest():
    def __init__(self, logger: Logger, queues: Queues):
        self.logger = logger
        self.mcu_writes = queues.mcu_writes
        self.encoder_reads = queues.encoder_reads

        self.test_speed = 0.5 # Set a reasonable test speed


    async def observe_encoder(self, motor_index: int, duration: float = 2.0):
        encoder_values = []

        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < duration:
            try:
                #Wait for encoder data with a short timeout so the loop can continue
                msg = await asyncio.wait_for(self.encoder_reads.get(), timeout=0.2)

                if msg.get("motor") == motor_index:
                    encoder_values.append(msg.get("encoder_value"))

            except asyncio.TimeoutError:
                continue
        return encoder_values


    async def test_motors(self):
        try:
            for motor_index in range(4):
                self.logger.log.info(f"Testing motor {motor_index}")

                #Set speed for the current motor
                speed_command = {f"speed{motor_index}": self.test_speed}
                await self.mcu_writes.put(speed_command)
                
                #Start collecting encoder readings
                observe_task = asyncio.create_task(self.observe_encoder(motor_index, duration=2))

                #Wait to observe motor behavior
                await asyncio.sleep(2) #Two seconds

                #Stop the motor
                stop_command = {f"speed{motor_index}": 0.0}
                await self.mcu_writes.put(stop_command)

                #Wait for encoder observation to complete
                encoder_values = await observe_task


                self.logger.log.info(f"Motor {motor_index} test completed. Encoder reading {encoder_values}")

            self.logger.log.info("All motors tested successfully")

        except Exception as e:
            self.logger.log.error(f"Error during motor testing: {e.__class__.__name__}")
        except asyncio.CancelledError:
            self.logger.log.info("Motor testing cancelled.")