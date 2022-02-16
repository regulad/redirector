"""
Regulad's aiohttp-mongodb-base
https://github.com/regulad/aiohttp-mongodb-base

If you want to run the webserver with an external provisioning/management system like Gunicorn,
run the awaitable create_app.
"""

from typing import Mapping
import logging
from os import environ

from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorClient

from routes import ROUTES
from utils.middlewares import *
from utils.signals import *


CONFIGURATION_PROVIDER: Mapping[str, str] = environ
CONFIGURATION_KEY_PREFIX: str = "EXAMPLE"
# This could be a JSON or YAML file if you want to to be.


async def create_app():
    """Create an app and configure it."""

    # Create the app
    app = web.Application(middlewares=MIDDLEWARE_CHAIN)

    # Config
    app["database_connection"] = AsyncIOMotorClient(
        CONFIGURATION_PROVIDER.get(f"{CONFIGURATION_KEY_PREFIX}_URI", "mongodb://mongo")
    )
    app["database"] = app["database_connection"][
        CONFIGURATION_PROVIDER.get(
            f"{CONFIGURATION_KEY_PREFIX}_DB", CONFIGURATION_KEY_PREFIX
        )
    ]

    # Routes
    app.add_routes(ROUTES)

    # Signals
    app.on_response_prepare.extend(ON_RESPONSE_PREPARE_SIGNALS)

    # Off we go!
    return app


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s:%(levelname)s:%(name)s: %(message)s"
    )

    port = int(CONFIGURATION_PROVIDER.get(f"{CONFIGURATION_KEY_PREFIX}_PORT", "8081"))
    host = CONFIGURATION_PROVIDER.get(f"{CONFIGURATION_KEY_PREFIX}_HOST", "0.0.0.0")

    web.run_app(create_app(), host=host, port=port)
