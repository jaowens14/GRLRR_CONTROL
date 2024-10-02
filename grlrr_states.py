from grlrr_state import State
import asyncio

class Initializing(State):
    def on_event(self, event):
        match event:
            case 'initialization_complete':
                return Waiting()
            case _:
                print('Initi state default case')
        return self
    

class Waiting(State):
    def on_event(self, event):
        match event:
            case 'process_started':
                return Running()
            case _:
                print('waiting state default case')
        return self
    
    async def waiting():
        while True:
            print("waiting")
            await asyncio.sleep(1)
    

class Running(State):
    def on_event(self, event):
        match event:
            case 'process_stopped':
                return Waiting()
            case _:
                print('running state default case')
        return self
    
    async def running():
        while True:
            print("running")
            await asyncio.sleep(1)