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
        self.queues = [self.images, self.angles, self.offsets, self.responses, self.commands, self.mcu_writes, self.mcu_reads]

    async def check_queues(self):
        while True:
            for q in self.queues:
                if q.full():
                    print(q, " is full")  
                    await asyncio.sleep(10)  
            await asyncio.sleep(1)