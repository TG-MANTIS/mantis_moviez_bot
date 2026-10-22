from aiohttp import web

async def web_server():
    app = web.Application()
    routes = web.RouteTableDef()

    @routes.get("/", allow_head=True)
    async def root_route_handler(request):
        return web.Response(text="Bot is Alive!")

    app.add_routes(routes)
    return app
