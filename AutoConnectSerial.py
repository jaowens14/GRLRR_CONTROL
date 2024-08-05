
import serial
import asyncio
import fnmatch
import glob
from logger import grlrr_log

import SerialMessager


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

            if is_h7(connected_device):
                return connected_device
            
    except Exception as e:
        # send alert to the tablet
        grlrr_log.info(e)

def is_h7(h7):
    try:
        sm = SerialMessager.SerialMessager(h7)
        print("hello")
        
        sm.command_queue.insert(0, {"device": "?"})

    except Exception as e:
        grlrr_log.info(e)


connect_serial(detect_serial())
