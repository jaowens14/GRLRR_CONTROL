import asyncio
from aioconsole import ainput
from queues import command_queue

async def run_quick_stop_service():
    while True:
        if await ainput(">>>") == '':
            grlrr_off()


def grlrr_off():
    command_queue = asyncio.Queue(10)
    command_queue.put_nowait({"msgtyp":"set", "motorSpeed0": -1.0 * float(0.0), 
                                   "motorSpeed1": -1.0 * float(0.0),
                                   "motorSpeed2": float(0.0),
                                   "motorSpeed3": float(0.0)})
    asyncio.sleep(1)
    quit()