import glob
import fnmatch
import serial
import json
import asyncio
from logger import Logger
from queues import Queues
from my_redis import MyRedis
import traceback


class SerialServer():
    def __init__(self, logger: Logger, queues: Queues):
        self.logger = logger
        self.mcu_reads = queues.mcu_reads
        self.mcu_writes = queues.mcu_writes
        self.distances    = queues.distances
        # self.mcu_writes.put_nowait({"msgtyp": "get", "device":"?", "motorSpeed":0})
        self.mcu_writes.put_nowait({"start_serial":      1})
        self.mcu_writes.put_nowait({"speed0": -1.0 * float(0.0)})
        self.mcu_writes.put_nowait({"speed1": -1.0 * float(0.0)})
        self.mcu_writes.put_nowait({"speed2":        float(0.0)})
        self.mcu_writes.put_nowait({"speed3":        float(0.0)})
        self.mcu = None

    def detect_serial(self, preferred_list=['*']):
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

    def connect_serial(self, available_ports):
        try:
            connected_device = serial.Serial(
                available_ports[0], 115200, timeout=0.01)
            if connected_device.isOpen():
                self.logger.log.info(
                    "serial connected to "+str(available_ports[0]))
                return connected_device
            else:
                raise Exception("No serial devices")
        except Exception as e:
            # send alert to the tablet
            self.logger.log.info(e)

    def valididate_serial(self, device):
        try:
            msg = {"msgtyp": "get", "device": "?"}
            device.write((json.dumps(msg)+'\n').encode('ascii'))
            new_msg = json.loads(device.read_until(
                expected=b"\n").decode('ascii'))
            self.logger.log.info(new_msg)
            if new_msg["device"] == "h7":
                self.logger.log.info("h7 connected")
                return 1
            else:
                self.logger.log.error("NOT CONNECTED")
                return 0
        except Exception as e:
            self.logger.log.error(e)
            self.logger.log.error(
                "no valid device / comm issue / no api endpoint")







    async def run(self):
        self.mcu = self.connect_serial(self.detect_serial())
        if self.mcu:
            await asyncio.gather(self.send(), self.receive(), self.hb())
        else:
            self.logger.log.info(
                "Unable to connect to serial device. Exiting...")
            quit()

    async def send(self):
        while True:
            msg = await self.mcu_writes.get()
            self.mcu.write(('<'+json.dumps(msg)+'>').encode('ascii'))

    async def hb(self):
        while True:
            await asyncio.sleep(0.25)
            await self.mcu_writes.put({"hb": 1})


    async def receive(self):
        while True:
            try:

                msg = self.mcu.read_until('\n').decode('ascii')
                #print('"'+msg+'"')

                if msg:
                    msg_dict = json.loads(msg)
                    #print(msg_dict)
                    if msg_dict:
                        self.logger.log.debug(msg_dict)
                        await self.distances.put(msg_dict['distance'])
                        #test = await self.distances.get()
            
            except json.JSONDecodeError as err:
                # typical string debug
                self.logger.log.debug(msg)
                
            await asyncio.sleep(0)
