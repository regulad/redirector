import logging
from urllib.parse import urlparse

from aiohttp import web

from utils.database import Document

ROUTES: web.RouteTableDef = web.RouteTableDef()


@ROUTES.post("/{id}")
async def set_link(request: web.Request):
    link_id: str = request.match_info["id"]
    link_doc: Document = await Document.get_document(request.app["database"]["links"], {"_id": link_id})

    redirect_to: str = await request.text()

    try:
        urlparse(redirect_to)
    except ValueError:
        raise web.HTTPBadRequest(reason="Invalid redirect URL")

    await link_doc.update_db({"$set": {"redirect_to": redirect_to}})

    logging.info(f"Will redirect {request.remote} at {link_id} to {redirect_to}")

    raise web.HTTPCreated(reason="Link created")


@ROUTES.get("/{id}")
async def get_link(request: web.Request):
    link_id: str = request.match_info["id"]
    link_doc: Document = await Document.get_document(request.app["database"]["links"], {"_id": link_id})

    if link_doc.get("redirect_to") is None:
        raise web.HTTPNotFound(reason="Link not found")

    redirect_to: str = link_doc["redirect_to"]

    logging.info(f"Redirecting {request.remote} at {link_id} to {redirect_to}")

    return web.HTTPFound(location=redirect_to)


__all__ = ["ROUTES"]
