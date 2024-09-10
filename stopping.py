import asyncio
from logger import grlrr_log
from queues import command_queue


async def check_for_keyboard_interrupt():

    while True:
    

            # m1 is the left side right now, m4 is the right side
            cmd = {"msgtyp":"set", "motorSpeed0": -1.0 * float(0.0), 
                                   "motorSpeed1": -1.0 * float(0.0),
                                   "motorSpeed2": float(0.0),
                                   "motorSpeed3": float(0.0)}
            await command_queue.put(cmd)