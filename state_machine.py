

import asyncio
from logger import Logger
from queues import Queues
from tasks import Tasks

class StateMachine():
    def __init__(self, logger:Logger, queues:Queues, tasks:Tasks):
        self.logger = logger
        self.commands = queues.commands
        self.tasks = tasks.tasks

    async def run(self):
        while True:
            cmd = await self.commands.get()

            if 'start_process' in cmd:


            await asyncio.Future()  