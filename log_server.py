from logger import grlrr_log
from aiohttp import web

async def handle(request):
    f_served = open('grlrr.log','rb')
    f_content = f_served.read().decode('utf-8')
    f_served.close()
    return web.Response(text=f_content)

async def run_log_server():
    grlrr_log.info("log server started")
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 1095)
    await site.start()

