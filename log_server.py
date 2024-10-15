from aiohttp import web
from logger import Logger


class LogServer():
    def __init__(self, logger: Logger):
        self.logger = logger

    async def handle(self, request):
        f_served = open(self.logger.log.file_name,'rb')
        f_content = f_served.read().decode('utf-8')
        f_served.close()
        return web.Response(text=f_content)


    async def run(self):
        app = web.Application()
        app.add_routes([web.get('/', self.handle)])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 1095) # 1095 looks like logs
        await site.start()


    