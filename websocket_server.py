import asyncio
import json
from websockets.server import serve
from logger import grlrr_log
from queues import command_queue, result_queue
from camera_server import image_queue
import datetime
async def run_websocket_server():
    async with serve(connection_handler, "0.0.0.0", 5000):
        await asyncio.Future() # runs server forever


async def connection_handler(websocket):

    await asyncio.gather(
        consumer_handler(websocket),
        producer_handler(websocket),
    )

# receive the messages 
async def consumer_handler(websocket):
    async for message in websocket:
        await consumer(message)


# send the messages
async def producer_handler(websocket):
    while True:
        message = await producer()
        # normal
        #await websocket.send(str(message))
        # used for sending images to viewer
        await websocket.send(message)
        


async def consumer(packet):
    # get info from the h7
    getPacket = {"msgtyp":"get"}
    try:
        grlrr_log.info("websocket packet: ")
        grlrr_log.info(packet)
        packet = json.loads(packet)
        motorSpeedPacket = None
        motorSpeedPacket = {"msgtyp":"set", "motorSpeed0": -1.0 * float(packet.get("motorSpeed0")), 
                                            "motorSpeed1": -1.0 * float(packet.get("motorSpeed1")),
                                            "motorSpeed2": float(packet.get("motorSpeed2")),
                                            "motorSpeed3": float(packet.get("motorSpeed3"))}
    except Exception as e:
        grlrr_log.info("unable to parse command")
    await command_queue.put( getPacket)
    if motorSpeedPacket:
        await command_queue.put( motorSpeedPacket)
    


async def producer():
    #print("producer fired")
    return await image_queue.get()
    #return datetime.datetime.now()






