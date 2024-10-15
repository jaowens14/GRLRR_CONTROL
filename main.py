import os
from grlrr import Grlrr
from logger import Logger
from tasks import Tasks
from queues import Queues
from log_server import LogServer
from websocket_server import WebsocketServer
from serial_server import SerialServer
from camera_server import CameraServer
from steering import Steering
from state_machine import StateMachine

def main():
    
    l   = Logger()
    ts = Tasks()
    qs  = Queues()
    ls  = LogServer(logger = l)
    wss = WebsocketServer(logger=l, queues = qs)
    ss = SerialServer(logger=l, queues=qs)
    cs = CameraServer(logger=l, queues=qs)
    s = Steering(logger=l, queues=qs)

    sm = StateMachine(logger=l, queues=qs, tasks=ts)

    grlrr = Grlrr( logger = l, 
                   tasks = ts,
                   queues = qs,
                   log_server = ls,
                   websocket_server = wss,
                   serial_server = ss,
                   camera_server = cs,
                   steering = s,
                   state_machine = sm,
                    )
    l.log.info('grlrr.run()')
    grlrr.run()

if __name__ == "__main__":
    PID = str(os.getpid())
    with open('.grlrr.pid', 'w') as file:
        file.write(PID)
        file.close()
    main()

