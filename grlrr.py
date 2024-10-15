import asyncio

from logger import Logger
from tasks import Tasks
from log_server import LogServer
from queues import Queues
from websocket_server import WebsocketServer
from serial_server import SerialServer
from camera_server import CameraServer
from steering import Steering
from state_machine import StateMachine
class Grlrr():
    def __init__(self, 
                 logger: Logger, 
                 tasks: Tasks,
                 queues: Queues,
                 log_server: LogServer,
                 websocket_server: WebsocketServer,
                 serial_server: SerialServer,
                 camera_server: CameraServer,
                 steering: Steering,
                 state_machine: StateMachine,):

        self.images     = queues.images
        self.angles     = queues.angles
        self.offsets    = queues.offsets
        self.responses  = queues.responses
        self.commands   = queues.commands
        self.mcu_writes = queues.mcu_writes
        self.mcu_reads  = queues.mcu_reads
        self.queues = queues
        self.tasks = tasks.tasks
        self.logger = logger
        self.log_server = log_server
        self.websocket_server = websocket_server
        self.serial_server = serial_server
        self.camera_server = camera_server
        self.steering_server = steering
        self.state_machine = state_machine

    def run(self):
        self.logger.log.info("GRLRR STARTED")
        asyncio.run(self.create_tasks(), debug=True)

    async def create_tasks(self):
        async with asyncio.TaskGroup() as tg:
            self.tasks['log_server'] =    tg.create_task(self.log_server.run()      , name = 'log_server')
            self.tasks['websockets'] =    tg.create_task(self.websocket_server.run(), name = 'websockets')
            self.tasks['queues'] =        tg.create_task(self.queues.check_queues() , name = 'queues')
            self.tasks['state_machine'] = tg.create_task(self.state_machine.run()   , name = 'state_machine')
