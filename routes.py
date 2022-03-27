import asyncio
import logging
from datetime import datetime
from urllib.parse import urlparse

from aiohttp import web, ClientSession
from motor.motor_asyncio import AsyncIOMotorCursor

from utils.database import Document

ROUTES: web.RouteTableDef = web.RouteTableDef()


async def handle_webhook(
        webhook_url: str,
        redirect_to: str,
        link_id: str,
        request: web.Request,
        started_processing: datetime
) -> None:
    try:
        async with ClientSession() as session:
            await session.post(webhook_url, json={"link_id": link_id, "redirected_to": redirect_to,
                                                  "timestamp": started_processing.isoformat(),
                                                  "remote": request.remote})
    except Exception:
        pass  # This ain't our problem.


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


@ROUTES.post("/webhook/{id}")
async def register_webhook(request: web.Request):
    link_id: str = request.match_info["id"]
    link_doc: Document = await Document.get_document(request.app["database"]["links"], {"_id": link_id})

    if link_doc.get("redirect_to") is None:
        raise web.HTTPNotFound(reason="Link not found")
    else:
        webhook_url: str = await request.text()

        await link_doc.update_db({"$set": {"webhook_url": webhook_url}})

        logging.info(f"{request.remote} registered webhook {webhook_url} for {link_id}")

        return web.HTTPOk(reason="Webhook registered")


@ROUTES.delete("/{id}")
async def delete_link(request: web.Request):
    link_id: str = request.match_info["id"]
    link_doc: Document = await Document.get_document(request.app["database"]["links"], {"_id": link_id})

    if link_doc.get("redirect_to") is None:
        raise web.HTTPNotFound(reason="Link not found")
    else:
        await link_doc.delete_db()

        logging.info(f"{request.remote} deleted {link_id}")

        return web.HTTPOk(reason="Link deleted")


@ROUTES.get("/data/{id}")
async def get_data(request: web.Request):
    link_id: str = request.match_info["id"]
    link_doc: Document = await Document.get_document(request.app["database"]["links"], {"_id": link_id})

    if link_doc.get("redirect_to") is None:
        raise web.HTTPNotFound(reason="Link not found")
    else:
        logging.info(f"Providing info of {link_id} to {request.remote}")

        cloned_doc: dict = dict(link_doc)
        cloned_doc.pop("_id")
        cloned_doc["last_access"] = cloned_doc["last_access"].isoformat()

        return web.json_response(cloned_doc)


@ROUTES.get("/hits/{id}")
async def get_hits(request: web.Request):
    many_hits: AsyncIOMotorCursor = request.app["database"]["hits"].find({"link_id": request.match_info["id"]})

    hits_list: list = await many_hits.to_list(length=None)

    # Inefficient!
    sorted_hits: list = sorted(hits_list, key=lambda hit: hit["timestamp"], reverse=True)

    for hit in sorted_hits:
        hit.pop("_id")
        hit["timestamp"] = hit["timestamp"].isoformat()

    return web.json_response(sorted_hits)


@ROUTES.get("/{id}")
async def get_link(request: web.Request):
    started_processing: datetime = datetime.now()

    link_id: str = request.match_info["id"]
    link_doc: Document = await Document.get_document(request.app["database"]["links"], {"_id": link_id})

    if link_doc.get("redirect_to") is None:
        raise web.HTTPNotFound(reason="Link not found")
    else:
        redirect_to: str = link_doc["redirect_to"]

        await link_doc.update_db(
            {"$set": {"last_access": started_processing, "last_remote": request.remote}, "$inc": {"hits": 1}}
        )

        await request.app["database"]["hits"].insert_one(
            {"link_id": link_id, "redirected_to": redirect_to, "timestamp": started_processing,
             "remote": request.remote}
        )

        if link_doc["webhook_url"] is not None:
            asyncio.create_task(
                handle_webhook(link_doc["webhook_url"], redirect_to, link_id, request, started_processing)
            )

        logging.info(f"Redirecting {request.remote} at {link_id} to {redirect_to}")

        return web.HTTPFound(location=redirect_to)


__all__ = ["ROUTES"]
