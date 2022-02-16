from aiohttp import web


ROUTES: web.RouteTableDef = web.RouteTableDef()


@ROUTES.get("/")
async def get_docs(request: web.Request):
    with open("README.md") as documentation:
        return web.json_response(list(line.strip() for line in documentation.readlines()))


__all__ = ["ROUTES"]
