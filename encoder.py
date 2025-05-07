import asyncio
import json
from logger import Logger
from queues import Queues

# This script is designed to listen for encoder readings from the queue of our four drive motors and average them.
# We want to allow the capability to actuate our shovel actuators based off of the encoder information.
#When the averaged encoder value hits specific threshold values (A,B,C,...) it will signal an actuator.

class Encoder:
    def __init__(self, logger: Logger, queues: Queues):
        """Initialize the Encoder wrapper with a logger and relevant queues."""
        self.logger = logger
        self.mcu_writes = queues.mcu_writes
        self.encoder_queue = queues.encoder_reads

    async def read_encoder(self):
        """Send a command to request the current encoder position and await the response"""
        command = {"action": "read_encoder"}
        await self.mcu_writes.put(command)
        self.logger.log.info("Sent encoder read request.")

        encoder_value = None
        try:
            #Wait for a numeric value response
            while encoder_value is None:
                msg = await asyncio.wait_for(self.encoder_queue.get(), timeout=2.0)
                if isinstance(msg, (int, float)):
                    encoder_value = msg
        except asyncio.TimeoutError:
            self.logger.log.error("Timeout waiting for encoder position")
            return None
        
        self.logger.log.info(f"Recieved encoder position: {encoder_value}")
        return encoder_value
    
    async def reset_encoder(self):
        """Send a command to reset the encoder and await for confirmation."""
        command = {"action": "reset_encoder"}
        await self.mcu_writes.put(command)
        self.logger.log.info("Sent encoder reset command.")

        reset_confirmed = False
        try:
            while not reset_confirmed:
                msg = await asyncio.wait_for(self.encoder_queue.get(), timeout=2.0)
                if isinstance(msg, dict) and msg.get("status") == "Encoder reset":
                    reset_confirmed = True
        except asyncio.TimeoutError:
            self.logger.log.error("Timeout waiting for encoder reset confirmation.")
            return False
        
        self.logger.log.info("Encoder reset confirmed.")
        return True