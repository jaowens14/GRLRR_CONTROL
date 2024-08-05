import asyncio
import serial.threaded
from websockets.server import serve
from logger import grlrr_log
import serial
import fnmatch
import glob
import json



async def main():
    await asyncio.gather(websocket_server(), serial_server())



async def websocket_server():
    async with serve(connection_handler, "0.0.0.0", 8080):
        await asyncio.Future() # runs server forever



async def connection_handler(websocket):
    async for packet in websocket:
        grlrr_log.info("websocket packet: ")
        grlrr_log.info(packet)
        packet = json.loads(packet)
        motorSpeedPacket = {"device":"?", "motorSpeed":float(packet.get("motorSpeed"))}
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
        msg = {"device":"?"}
        device.write((json.dumps(msg)+'\n').encode('ascii'))
        new_msg = json.loads(device.read_until(expected=b"\n").decode('ascii'))

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
                e

            await asyncio.sleep(0)
        


grlrr_log.info("=============================================================")
grlrr_log.info("GRLRR STARTED")
grlrr_log.info("=============================================================")

command_queue = [{"device":"?", "motorSpeed":0}] 
result_queue = []

asyncio.run(main())

# {"wheelDiameter":"0.05","motorDirection":2,"motorSpeed":"0","motorMode":false,"motorEnable":true,"targetGlueHeight":"0","UT_Kp":"0.05","UT_Ki":"0.0","UT_Kd":"0.0","M_Kp":"25.0","M_Ki":"15.0","M_Kd":"0.0","ultrasonicValue":0,"batteryLevel":0,"estop":false,"uptime":0}