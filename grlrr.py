import asyncio
from logger import Logger
from log_server import LogServer
from websocket_server import WebsocketServer
from state_machine import StateMachine
from serial_server import SerialServer

class Queues():
    def __init__(self):
        self.images = asyncio.Queue(10)
        self.angles = asyncio.Queue(10)
        self.offsets = asyncio(10)
        self.responses = asyncio.Queue(10)
        self.commands = asyncio.Queue(10)
        self.mcu_write = asyncio.Queue(10)
        self.mcu_read = asyncio.Queue(10)

class Grlrr():
    
    def __init__(self):
        self.initialize_queues()
        self.initialize_state()
        self.initialize_modules()


    def run(self):
        '''the robot does tasks'''
        self.logger.log.info("GRLRR STARTED")
        asyncio.run(self.create_tasks(), debug=True)

    async def create_tasks(self):
        async with asyncio.TaskGroup() as tg:
            log_server_task = tg.create_task(self.log_server.run())
            websocket_server_task = tg.create_task(self.websocket_server.run())
            state_machine_task = tg.create_task(self.state_machine.run())
            serial_server_task = tg.create_task(self.serial_server.run())

    def initialize_queues(self):
        self.qs = Queues()


    def initialize_state(self):
        self.state_machine = StateMachine(self.qs)

    def initialize_modules(self):
        self.logger = Logger()
        self.log_server = LogServer(self.logger)
        self.websocket_server = WebsocketServer(self.logger, self.qs)
        self.serial_server = SerialServer(self.logger, self.qs)


