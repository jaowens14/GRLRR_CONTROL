#queues.py
import asyncio
class Queues():
    def __init__(self):
        self.images = asyncio.Queue(10)
        self.angles = asyncio.Queue(10)
        self.offsets = asyncio.Queue(10)
        self.responses = asyncio.Queue(10)
        self.commands = asyncio.Queue(10)
        self.mcu_writes = asyncio.Queue(10)
        self.mcu_reads = asyncio.Queue(10)


