from logger import grlrr_log
import glob
import fnmatch
import serial
import json
import asyncio
from main import command_queue, result_queue

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
        connected_device = serial.Serial(available_ports[0], 115200, timeout=0.01)
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
        grlrr_log.info(new_msg)
        if new_msg["device"] == "h7":
            grlrr_log.info("h7 connected")
            return 1
        else:
            grlrr_log.error("NOT CONNECTED")
            return 0
    except Exception as e:
        grlrr_log.error(e)
        grlrr_log.error("no valid device / comm issue / no api endpoint")


async def run_serial_server():

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