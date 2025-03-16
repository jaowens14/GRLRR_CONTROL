import asyncio
import json
import websockets.exceptions
from websockets.server import serve
from logger import Logger
from queues import Queues
    
class WebsocketServer():
    def __init__(self, logger:Logger, queues:Queues):
        self.logger = logger
        self.images = queues.images
        self.commands = queues.commands
        self.angles    = queues.angles
        self.offsets   = queues.offsets
        self.responses = queues.responses
        self.mcu_reads = queues.mcu_reads
        self.mcu_writes = queues.mcu_writes
        self.connected = False
        self.shutdown_event = asyncio.Event()
        #self._active_connections = set[WebsocketServerProtocol] = set()
    
    async def run(self):
        async with serve(self.connection_handler, "0.0.0.0", 5000):
            await self.shutdown_event.wait()

    async def connection_handler(self, websocket):
        await asyncio.gather(
            self.consumer(websocket),
            self.image_producer(websocket),
            self.response_producer(websocket),
        )
        self.shutdown_event.set()

#==============================================================
# message receiver
#==============================================================
# receive the messages / commands from the tablet
    async def consumer(self, websocket):
        try:
            async for message in websocket:
                self.connected = True
                await self.consumer_handler(message)
        except websockets.exceptions.ConnectionClosedError:
            self.connected = False


    async def consumer_handler(self, packet):
        self.logger.log.info(packet)
        cmd = json.loads(packet)
        await self.commands.put(cmd)
        await self.responses.put(cmd)


    async def image_producer(self, websocket):
        while True:
            image = await self.images.get()
            #angle = await self.angles.get()
            #offset = await self.offsets.get()
            
            await websocket.send(json.dumps({'image': image}))


    async def response_producer(self, websocket):
        while True:
            response = await self.responses.get()
            await websocket.send(json.dumps({'response':response}))

            #response = await self.mcu_reads.get()
            #await websocket.send(json.dumps({'mcu_reads':response}))


