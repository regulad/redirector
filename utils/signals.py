from aiohttp import web


async def set_response_headers(request: web.Request, response: web.Response) -> None:
    """Set the response headers into the response."""

    response.headers.update(request["response_headers"])


ON_RESPONSE_PREPARE_SIGNALS: list = [set_response_headers]


__all__ = ["ON_RESPONSE_PREPARE_SIGNALS"]
