import glob
import fnmatch
import serial
import json
import asyncio
from logger import Logger
from queues import Queues
import traceback


class SerialServer():
    def __init__(self, logger: Logger, queues: Queues):
        self.logger = logger
        self.mcu_reads = queues.mcu_reads
        self.mcu_writes = queues.mcu_writes
        self.distance = queues.distance
        self.feedback_reads = queues.feedbackSignals
        self.encoder_distance = queues.encoder_distance


        # self.mcu_writes.put_nowait({"msgtyp": "get", "device":"?", "motorSpeed":0})
        self.mcu_writes.put_nowait({"start_serial":      1})
        self.mcu_writes.put_nowait({"speed0": -1.0 * float(0.0)})
        self.mcu_writes.put_nowait({"speed1": -1.0 * float(0.0)})
        self.mcu_writes.put_nowait({"speed2":        float(0.0)})
        self.mcu_writes.put_nowait({"speed3":        float(0.0)})

        # Initialize actuators
        self.mcu_writes.put_nowait({'action': 'set_voltage', 'channel': 0, 'voltage': 0})
        self.mcu_writes.put_nowait({'action': 'set_voltage', 'channel': 1, 'voltage': 0})
        self.mcu_writes.put_nowait({'action': 'set_voltage', 'channel': 2, 'voltage': 0})


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
                available_ports[0], 115200, timeout=10.00)

            if connected_device.isOpen():
                self.logger.log.info("serial connected to "+str(available_ports[0]))
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
            
    def clear_serial(self):
        self.mcu.reset_input_buffer()
        self.mcu.reset_output_buffer()

    async def run(self):
        self.mcu = self.connect_serial(self.detect_serial())
        if self.mcu:
            self.clear_serial()

            #Temporarily removed the heartbeat message.
            await asyncio.gather(self.send(), self.receive())

            #await asyncio.gather(self.send(), self.receive(), self.hb())
        else:
            self.logger.log.info("Unable to connect to serial device. Exiting...")
            quit()

    async def send(self):
        while True:
            msg = await self.mcu_writes.get()

            self.logger.log.info(f"Sending: {msg}")

            try:
                self.mcu.write(('<'+json.dumps(msg)+'>').encode('ascii'))
            except Exception as e:
                self.logger.log.error(f"Error sending data: {e}")

    async def hb(self):
        while True:
            await self.mcu_writes.put({"hb": 1})
            await asyncio.sleep(0.75)

    #async def parse_dict(self, msg_dict):
    #    if 'distance' in msg_dict:
    #        await self.distance.put(msg_dict['distance'])


    async def receive(self):
        while True:
            try:
                line = self.mcu.readline().decode('ascii').strip()
                #self.logger.log.info(f"Raw serial line: {line}")
                msg_dict = json.loads(line)

                # Debug log the received message
                #self.logger.log.info(f"Received: {msg_dict}")
                
                # Handle distance sensor updates
                if 'distance' in msg_dict:
                    await self.distance.put(msg_dict['distance'])
                    self.logger.log.info(f"New sensor distance: {msg_dict['distance']}")

                # Handle actuator feedback updates
                if 'feedback' in msg_dict:
                    await self.feedback_reads.put(msg_dict['feedback'])
                    self.logger.log.info(f"Actuator {msg_dict['channel']} feedback: {msg_dict['feedback']}")

                # Handle encoder position updates
                if 'encoder_distance' in msg_dict:
                    await self.encoder_distance.put(msg_dict['encoder_distance'])
                    self.logger.log.info(f"Encoder Position: {msg_dict['encoder_distance']}")

                # Handle encoder reset confirmation
                if 'status' in msg_dict and msg_dict['status'] == "Encoder Reset":
                    await self.encoder_distance.put(msg_dict)
                    self.logger.log.info("Encoder successfully reset.")
                    
            except json.JSONDecodeError as e:
                self.logger.log.error(f"JSON decode error: {e} - Raw data: {line}")
            except Exception as e:
                self.logger.log.error(f"Error parsing serial data: {e} - Raw data: {line}")
            await asyncio.sleep(0)