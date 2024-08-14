import asyncio

command_queue = asyncio.Queue(10)
result_queue = asyncio.Queue(10)
image_queue = asyncio.Queue(10)
