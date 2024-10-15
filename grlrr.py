import asyncio

from logger import Logger
from log_server import LogServer
from queues import Queues
from websocket_server import WebsocketServer
from serial_server import SerialServer
from camera_server import CameraServer
from steering import Steering

class Grlrr():
    def __init__(self, 
                 logger: Logger, 
                 queues: Queues,
                 log_server: LogServer,
                 websocket_server: WebsocketServer,
                 serial_server: SerialServer,
                 camera_server: CameraServer,
                 steering: Steering):

        self.images     = queues.images
        self.angles     = queues.angles
        self.offsets    = queues.offsets
        self.responses  = queues.responses
        self.commands   = queues.commands
        self.mcu_writes = queues.mcu_writes
        self.mcu_reads  = queues.mcu_reads
        #self.queues = queues
        self.tasks = set() #?
        self.logger = logger
        self.log_server = log_server
        self.websocket_server = websocket_server
        self.serial_server = serial_server
        self.camera_server = camera_server
        self.steering_server = steering


    def run(self):
        self.logger.log.info("GRLRR STARTED")
        asyncio.run(self.create_tasks(), debug=False)


    async def create_tasks(self):
        async with asyncio.TaskGroup() as tg:
            
            self.tasks.add(tg.create_task(self.log_server.run()))
            self.tasks.add(tg.create_task(self.websocket_server.run()))
            self.tasks.add(tg.create_task(self.serial_server.run()))
            self.tasks.add(tg.create_task(self.camera_server.run()))
            self.tasks.add(tg.create_task(self.steering_server.run()))
            #self.tasks.add(tg.create_task(self.queues.check_queues()))


