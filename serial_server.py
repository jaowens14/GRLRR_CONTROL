import glob
import fnmatch
import serial
import json
import asyncio

class SerialServer():
    def __init__(self, logger, qs):
        self.logger = logger
        self.mcu_read =  qs.mcu_read
        self.mcu_write = qs.mcu_write
        self.mcu_write.put_nowait({"msgtyp": "get", "device":"?", "motorSpeed":0})
        self.mcu_write.put_nowait({"msgtyp":"set", "motorSpeed0": -1.0 * float(0.0), 
                                   "motorSpeed1": -1.0 * float(0.0),
                                   "motorSpeed2": float(0.0),
                                   "motorSpeed3": float(0.0)})

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
            connected_device = serial.Serial(available_ports[0], 115200, timeout=0.01)
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
            msg = {"msgtyp":"get","device":"?"}
            device.write((json.dumps(msg)+'\n').encode('ascii'))
            new_msg = json.loads(device.read_until(expected=b"\n").decode('ascii'))
            self.logger.log.info(new_msg)
            if new_msg["device"] == "h7":
                self.logger.log.info("h7 connected")
                return 1
            else:
                self.logger.log.error("NOT CONNECTED")
                return 0
        except Exception as e:
            self.logger.log.error(e)
            self.logger.log.error("no valid device / comm issue / no api endpoint")


    async def run(self):
        h7 = self.connect_serial(self.detect_serial())
        if self.valididate_serial(h7):
            while True:
                try:
                    msg = await self.mcu_write.get()
                    #print("serial get fired")
                    self.logger.log.info("wrote to h7: ")
                    self.logger.log.info((json.dumps(msg)+'\n').encode('ascii'))
                    h7.write((json.dumps(msg)+'\n').encode('ascii'))
                    new_msg = h7.read_until(expected=b"\n").decode('ascii')
                    self.logger.log.info("recv from h7: ")
                    self.logger.log.info(new_msg)

                    self.mcu_read.put_nowait(new_msg)
                    # nothing to consume the results queue yet to this line was blocking
                    #await result_queue.put(json.loads(new_msg))
                    #print("serial put fired")

                except Exception as e:
                    self.logger.log.info(e)

                await asyncio.sleep(0)
        else:
            self.logger.log.info("Unable to connect to serial device. Exiting...")
            quit()