from logger import Logger
from log_server import LogServer
from queues import Queues
from websocket_server import WebsocketServer
from serial_server import SerialServer
from camera_server import CameraServer
from steering import Steering
import asyncio 

class Grlrr():
    def __init__(self):
        # varibale and object creation and organization
        self.logger   = Logger()
        self.qs  = Queues()
        self.log_server = LogServer( logger=self.logger)
        self.wss = WebsocketServer(  logger=self.logger, queues=self.qs)
        self.ss = SerialServer(      logger=self.logger, queues=self.qs)
        self.cs = CameraServer(      logger=self.logger, queues=self.qs)
        self.s = Steering(           logger=self.logger, queues=self.qs)
        self.logger.log.info("grlrr init")

    def setup(self):
        self.event_loop = asyncio.get_running_loop()
        self.logger.log.info('grlrr setup')
        self.event_loop.create_task(self.wss.run())
        self.event_loop.create_task(self.ss.run())
        self.event_loop.create_task(self.cs.run())
        self.event_loop.create_task(self.s.run())



    async def loop(self):
        while True:
            
            cmd = self.qs.commands.get()
            print('main loop')



            start = self.event_loop.time()
            await asyncio.sleep(1)
            print('duration: ', str(self.event_loop.time()-start))



    async def main(self):
        self.setup()
        await self.loop()



