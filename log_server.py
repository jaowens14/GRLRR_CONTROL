import asyncio
from aiohttp import web

async def handle(request):
    f_served = open('grlrr.log','rb')
    f_content = f_served.read()
    f_served.close()
    return web.Response(text=f_content)

async def run_log_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5555)
    await site.start()
