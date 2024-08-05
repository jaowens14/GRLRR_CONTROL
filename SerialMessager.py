
import json
import asyncio

class SerialMessager:
    def __init__(self, serial_connection):
        self.command_queue = [{"device": "?"}] 
        self.result_queue = []
        self.h7 = serial_connection
        self.start_serial()


    def new_command(self, ncmd):
        '''have a new command added from the system'''
        self.command_queue.insert(0, ncmd)
        print("commands: ", self.command_queue)
        print("reults: ", self.result_queue)

    async def start_serial(self):
        await asyncio.create_task(self.send_messages())
        await asyncio.create_task(self.recv_messages())

    async def write_msg(self, msg):
        '''write serial with new line'''
        return self.h7.write((json.dumps(msg)+'\n').encode('ascii'))


    async def send_messages(self):
        '''send messages to the h7'''
        while True:
            if len(self.command_queue):
                msg = self.command_queue.pop()
                await self.write_msg(msg)
            await asyncio.sleep(0.1)


    async def read_msg(self):
        '''Read serial until new line'''
        return self.h7.read_until(expected=b"\n").decode('ascii')


    async def recv_messages(self):
        '''store the data from the h7 for processing'''
        while True:
            new_msg = await self.read_msg()
            if new_msg:
                print(new_msg)
                self.result_queue.insert(0, json.loads(new_msg))
                if len(self.result_queue) > 3:
                    self.result_queue.pop()
            await asyncio.sleep(0.1)


