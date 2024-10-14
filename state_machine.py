import asyncio

class StateMachine():
    def __init__(self, qs):
        self.state = "initializing"
        self.commands = qs.commands
        self.responses = qs.responses

    def set_state(self, state):
        match state:
            case "initializing":
                print(" doing initial state")
            case "start_process":
                print("doing running")
            case "stop_process":
                print("stopping process")
            case _:
                print("ya don messed up")

    async def run(self):
        while True:
            cmd = await self.commands.get()
            print("updated command: ", cmd)
            self.set_state(cmd)
            await asyncio.sleep(0)