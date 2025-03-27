import asyncio
from logger import Logger
from queues import Queues

# This script is designed to listen for encoder readings from the queue of our four drive motors and average them.
# We want to allow the capability to actuate our shovel actuators based off of the encoder information.
#When the averaged encoder value hits specific threshold values (A,B,C,...) it will signal an actuator.

class EncoderAverager:
    def __init__(self, logger: Logger, encoder_queues: list):
        pass