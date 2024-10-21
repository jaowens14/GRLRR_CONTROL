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
        self.steering= Steering(           logger=self.logger, queues=self.qs)
        self.logger.log.info("grlrr init")
        self.cmd = 'initialize_robot'

    def setup(self):
        self.event_loop = asyncio.get_running_loop()
        self.logger.log.info('grlrr setup')
        self.event_loop.create_task(self.wss.run())
        self.event_loop.create_task(self.ss.run())
        self.event_loop.create_task(self.cs.run())


    def get_command(self):
        try:
            return self.qs.commands.get_nowait()
        except asyncio.QueueEmpty:
            pass
            #self.logger.log.debug('command queue empty')
        except Exception as e:
            self.logger.log.info('other exception')
            print(e.__class__.__name__)


    def change_state(self, cmd):
        match cmd:
            case 'initialize_robot':
                print('some init')
            case 'start_process':
                print('started process')
                self.steering_task = self.event_loop.create_task(self.steering.run())
            case 'stop_process':
                print('stopped process')
                self.steering_task.cancel()


            case None:
                return
                print('none case ...........')
            case _:
                return
                print('default')


    def update_state(self):
        new_cmd = self.get_command()
        if new_cmd != self.cmd:
            self.cmd = new_cmd
            self.change_state(new_cmd)





    async def loop(self):
        while True:
            
            self.update_state()
            #print('main loop')
            ##start = self.event_loop.time()
            #self.qs.show_queue_size()
            self.logger.log.info('main')
            await asyncio.sleep(1)
            #print('duration: ', str(self.event_loop.time()-start))




    async def main(self):
        self.setup()
        await self.loop()



