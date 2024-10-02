import asyncio
import json
from websockets.server import serve
from logger import grlrr_log
from queues import command_queue, result_queue, response_queue, state_queue
from camera_server import image_queue
import datetime




#==============================================================
# server setup
#==============================================================
async def run_websocket_server():
    await serve(connection_handler, "0.0.0.0", 5000)
        #await asyncio.Future() # runs server forever


async def connection_handler(websocket):
    await asyncio.gather(
        consumer(websocket),
        image_producer(websocket),
        response_producer(websocket),
    )



#==============================================================
# message receiver
#==============================================================
# receive the messages / commands from the tablet
async def consumer(websocket):
    async for message in websocket:
        await consumer(message)


# route the commands to the proper place
async def consumer(packet):
    try:
        await consumer_handler(json.loads(packet))

    except Exception as e:
        grlrr_log.info("unable to parse command")


# this json api is designed to work like this:
# the function assumes the type and sender and receiver
# data is just labled {"image":image_data}
async def consumer_handler(packet):

    # the server can receive:
    # 1. motion commands (move_forward, stop, move_backward)
    # 2. parameter setting commands (set_process_speed, use_steering)
    # 3. 

    match ''.join(packet.keys()):
        case 'stop':
            await response_queue.put("stopped")

        case 'start':
            await response_queue.put("started")

        case 'go_forward':
            await response_queue.put("going forward")

        case 'go_backward':
            await response_queue.put("going backward")

        case 'set_speed':
            await response_queue.put('set_speed')

        case 'use_steering':
            await response_queue.put('use_steering')
            
        case _:
            await response_queue.put("no response")
            await state_queue.put("stop")


#==============================================================
# message sender
#==============================================================
async def image_producer(websocket):
    while True:
        image = await image_queue.get()
        await websocket.send(json.dumps({"image": image}))


async def response_producer(websocket):
    while True:
        response = await response_queue.get()
        await websocket.send(json.dumps({"response":response}))






