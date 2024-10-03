import asyncio

from logger import Logger
from log_server import LogServer
from websocket_server import WebsocketServer
class Grlrr():
    '''represents the robot'''
    def __init__(self):
        '''the robot has modules'''

        self.logger = Logger()
        self.log_server = LogServer(self.logger)
        self.websocket_server = WebsocketServer(self.logger)
    def run(self):
        '''the robot does tasks'''
        self.logger.info("GRLRR STARTED")
        asyncio.run(self.create_tasks(), debug=True)


    async def create_tasks(self):
        await asyncio.gather( self.log_server.run(),

                                #self.state_machine.run(),
                                #self.websocket_server.run(),
                                #serial_server.run_serial_server(), 
                                #camera_server.run_camera_server(),
                                #steering.run_steering(),
                                
                                )
                                


