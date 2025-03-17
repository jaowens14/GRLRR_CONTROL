import asyncio
from logger import Logger
from queues import Queues

# This script is designed to listen for encoder readings from the queue of our four drive motors and average them.
# We want to allow the capability to actuate our shovel actuators based off of the encoder information. 