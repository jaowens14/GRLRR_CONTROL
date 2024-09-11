from logger import grlrr_log
import datetime
import asyncio

async def run_uptime_server():
    while True:
        grlrr_log.info(str(datetime.datetime.now()))
        await asyncio.sleep(60)
