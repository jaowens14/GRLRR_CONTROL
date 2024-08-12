import os
import asyncio

command_queue = [{"msgtyp": "get", "device":"?", "motorSpeed":0}] 
result_queue = []

# grlrr robot specific
import websocket_server
import serial_server
import log_server
from logger import grlrr_log





async def start_grlrr_tasks():

    await asyncio.gather(
        websocket_server.run_websocket_server(), 
        serial_server.run_serial_server(), 
        log_server.run_log_server(),
        )



def main():

    grlrr_log.info("=============================================================")
    grlrr_log.info("GRLRR STARTED")
    grlrr_log.info("=============================================================")

    asyncio.run(start_grlrr_tasks())



if __name__ == "__main__":
    PID = str(os.getppid())
    with open('grlrr.pid', 'w') as file:
        file.write(PID)
        file.close()
    main()

