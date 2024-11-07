# queues.py
import asyncio


class Queues():
    def __init__(self):
        self.distance = 0.0
        self.images = asyncio.Queue(10)
        self.angles = asyncio.Queue(10)
        self.offsets = asyncio.Queue(10)
        self.responses = asyncio.Queue(10)
        self.commands = asyncio.Queue(10)
        self.mcu_writes = asyncio.Queue(50)
        self.mcu_reads = asyncio.Queue(10)
        self.queues = [self.images, self.angles, self.offsets,
                       self.responses, self.commands, self.mcu_reads, self.mcu_writes]

    def show_queue_size(self):
        for q in self.queues:
            print(q.qsize())
        print()
