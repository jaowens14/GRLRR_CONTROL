import asyncio
import json
from websockets.server import serve
from logger import Logger
from queues import Queues

    
class WebsocketServer():
    def __init__(self, logger:Logger, queues:Queues):
        self.logger = logger
        self.images = queues.images
        self.commands = queues.commands
        self.responses = queues.responses
        

    async def run(self):
        async with serve(self.connection_handler, "0.0.0.0", 5000):
            await asyncio.Future() # runs server forever

    async def connection_handler(self, websocket):
        await asyncio.gather(
            self.consumer(websocket),
            self.image_producer(websocket),
            self.response_producer(websocket),
        )

    #==============================================================
    # message receiver
    #==============================================================
    # receive the messages / commands from the tablet
    async def consumer(self, websocket):
        async for message in websocket:
            await self.consumer_handler(message)
    # this json api is designed to work like this:
    # the function assumes the type and sender and receiver
    # data is just labled {"image":image_data}

    async def consumer_handler(self, packet):
        packet = json.loads(packet)
        # the server can receive:
        # 1. motion commands (move_forward, stop, move_backward)
        # 2. parameter setting commands (set_process_speed, use_steering)
        # 3. 
        cmd = ''.join(packet.keys())
        parameter =''.join(str(packet.values()))
        print("cmd", cmd)
        print("parameter", parameter)
        await self.commands.put(cmd)
        await self.responses.put(cmd)


    async def image_producer(self, websocket):
        while True:
            image = await self.images.get()
            
            await websocket.send(json.dumps({"image": image}))


    async def response_producer(self, websocket):
        while True:
            response = await self.responses.get()
            await websocket.send(json.dumps({"response":response}))


