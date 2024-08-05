import asyncio
from websockets.server import serve
from logger import grlrr_log




def start_websocket_server():
    asyncio.run(run_server())


async def run_server():
    grlrr_log.info("started websocket server")
    async with serve(connection_handler, "0.0.0.0", 8080):
        await asyncio.Future() 

    

async def connection_handler(websocket):
    grlrr_log.info("received connection")
    async for message in websocket:
        grlrr_log.info("got message")
        print(message)
        await process_packet(message)



async def process_packet(packet):
    grlrr_log.info(packet)





