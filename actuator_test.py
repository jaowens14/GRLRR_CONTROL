import asyncio
from logger import Logger
from queues import Queues
import smbus2
import time

# This script is created to test each actuator individually to ensur proper function.

class ActuatorTest ():
    def __init__(self, logger: Logger, queues: Queues):
        self.logger = logger
        self.mcu_writes = queues.mcu_writes
        self.feedbackSignals = queues.feedbackSignals

        self.test_voltage = 2.5 # Set a reasonable test voltage

        # I2C addresses
        self.MCP4728_ADDRESS = 0x60
        self.ADS1115_ADDRESS = 0x48

        # Initialize I2C bus
        self.bus = smbus2.SMBus(1)

    def set_dac_voltage(self, channel, voltage):
        # Convert voltage to DAC value (assuming 12-bit resolution)
        dac_value = int((voltage / 5.0) * 4095)
        # Write to DAC
        self.bus.write_i2c_block_data(self.MCP4728_ADDRESS, channel, [dac_value >> 8, dac_value & 0xFF])

    def read_adc(self, channel):
        config = 0x8483 | (channel <<12)
        self.bus.write_i2c_block_data(self.ADS1115_ADDRESS, 0x01, [config >> 8, config & 0xFF])
        time.sleep(0.1)
        # Read ADC value
        data = self.bus.read_i2c_block_data(self.ADS1115_ADDRESS, 0x00, 2)
        adc_value = (data[0] << 8) | data[1]
        return adc_value
    
    async def observe_feedback(self, actuator_index: int, duration: float = 2.0):
        feedback_values = []
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < duration:
            try:
                msg = await asyncio.wait_for(self.feedback_reads.get(), timeout=0.2)

                if msg.get("actuator") == actuator_index:
                    feedback_values.append(msg.get("feedback_value"))

            except asyncio.TimeoutError:
                continue
        return feedback_values
    
    async def test_actuators(self):
        try:
            for actuator_index in range(4):
                self.logger.log.info(f"Testing actuator {actuator_index}")

                # Set voltage for the current actuator
                self.set_dac_voltage(actuator_index, self.test_voltage)

                # Start collecting feedback readings
                observe_task = asyncio.create_task(self.observe_feedback(actuator_index, duration=2))

                # Wait to observe actuator behavior
                await asyncio.sleep(2)

                # Stop the actuator
                self.set_dac_voltage(actuator_index, 0.0)

                # Wait for feedback observation to complete
                feedback_values = await observe_task

                self.logger.log.info(f"Actuator {actuator_index} test completed. Feedback reading {feedback_values}")

                self.logger.log.info(f"All actuators tested successfully")

        except Exception as e:
            self.logger.log.error(f"Error during actuator testing: {e.__class__.__name__}")
        except asyncio.CancelledError: 
            self.logger.log.info("Actuator testing cancelled.")