import asyncio
import json
from websockets.server import serve
from logger import grlrr_log
from main import command_queue, result_queue


async def run_websocket_server():
    async with serve(connection_handler, "0.0.0.0", 8080):
        await asyncio.Future() # runs server forever


async def connection_handler(websocket):
    async for packet in websocket:
        grlrr_log.info("websocket packet: ")
        grlrr_log.info(packet)
        packet = json.loads(packet)
        motorSpeedPacket = {"msgtyp":"set", "motorSpeed0": -1.0 * float(packet.get("motorSpeed1")), 
                                            "motorSpeed1": -1.0 * float(packet.get("motorSpeed2")),
                                            "motorSpeed2": float(packet.get("motorSpeed3")),
                                            "motorSpeed3": float(packet.get("motorSpeed4"))}
        getPacket = {"msgtyp":"get"}

        
        command_queue.insert(0, getPacket)
        command_queue.insert(0, motorSpeedPacket)


