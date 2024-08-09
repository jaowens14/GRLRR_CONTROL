import asyncio
import serial.threaded
from websockets.server import serve
from logger import grlrr_log
import serial
import fnmatch
import glob
import json

import log_server

async def start_tasks():
    await asyncio.gather(websocket_server(), serial_server(), log_server.run_log_server())



async def websocket_server():
    async with serve(connection_handler, "0.0.0.0", 8080):
        await asyncio.Future() # runs server forever



async def connection_handler(websocket):
    async for packet in websocket:
        grlrr_log.info("websocket packet: ")
        grlrr_log.info(packet)
        packet = json.loads(packet)
        motorSpeedPacket = {"msgtyp":"set", "motorSpeed0": -1.0 * float(packet.get("motorSpeed")), 
                            "motorSpeed1": -1.0 * float(packet.get("motorSpeed")),
                            "motorSpeed2": float(packet.get("motorSpeed")),
                            "motorSpeed3": float(packet.get("motorSpeed"))}
        command_queue.insert(0, motorSpeedPacket)








def detect_serial(preferred_list=['*']):
    '''try to auto-detect serial ports on win32'''
    glist = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    ret = []

    # try preferred ones first
    for d in glist:
        for preferred in preferred_list:
            if fnmatch.fnmatch(d, preferred):
                ret.append(d)
    if len(ret) > 0:
        return ret
    # now the rest
    for d in glist:
        ret.append(d)
    return ret


def connect_serial(available_ports):
    try:
        connected_device = serial.Serial(available_ports[0], 115200,timeout=1)
        if connected_device.isOpen():
            grlrr_log.info("serial connected to "+str(available_ports[0]))
            return connected_device
        else:
            raise Exception("No serial devices")
    except Exception as e:
        # send alert to the tablet
        grlrr_log.info(e)

def valididate_serial(device):
    try:
        msg = {"msgtyp":"get","device":"?"}
        device.write((json.dumps(msg)+'\n').encode('ascii'))
        new_msg = json.loads(device.read_until(expected=b"\n").decode('ascii'))
        print(new_msg)
        if new_msg["device"] == "h7":
            grlrr_log.info("h7 connected")
            return 1
        else:
            return 0
    except Exception as e:
        grlrr_log.info(e)
        grlrr_log.info("no valid device / comm issue / no api endpoint")


async def serial_server():

    h7 = connect_serial(detect_serial())
    if valididate_serial(h7):
        while True:
            try:
                if len(command_queue):
                    msg = command_queue.pop()
                    grlrr_log.info("wrote to h7: ")
                    grlrr_log.info((json.dumps(msg)+'\n').encode('ascii'))
                    h7.write((json.dumps(msg)+'\n').encode('ascii'))
                    new_msg = h7.read_until(expected=b"\n").decode('ascii')
                    if new_msg:
                        grlrr_log.info("recv from h7: ")
                        grlrr_log.info(new_msg)
                        result_queue.insert(0, json.loads(new_msg))
            except Exception as e:
                grlrr_log.info(e)

            await asyncio.sleep(0)
    else:
        grlrr_log.info("Unable to connect to serial device. Exiting...")
        quit()
        


grlrr_log.info("=============================================================")
grlrr_log.info("GRLRR STARTED")
grlrr_log.info("=============================================================")

command_queue = [{"device":"?", "motorSpeed":0}] 
result_queue = []

def main():
    # start the tasks
    asyncio.run(start_tasks())
