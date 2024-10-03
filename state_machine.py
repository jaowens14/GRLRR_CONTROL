
import asyncio

class StateMachine():
    def __init__(self):
        self.state = "initializing"

    def set_state(self, state):
        print("state change")
        self.state = state

    
    async def run(self):
        while True:
            match self.state:
                case "initializing":
                    print(" doing initial state")
                case "start_process":
                    print("doing running")
                case "stop_process":
                    self.wss.kill_websocket()
                case _:
                    print("ya don messed up")
            await asyncio.sleep(1)

