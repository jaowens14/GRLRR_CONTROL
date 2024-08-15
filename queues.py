import asyncio

command_queue = asyncio.Queue(10)
result_queue = asyncio.Queue(10)
image_queue = asyncio.Queue(10)
angle_queue = asyncio.Queue(10)
left_offset_queue = asyncio.Queue(10)
right_offset_queue = asyncio.Queue(10)
control_inputs = asyncio.Queue(10)