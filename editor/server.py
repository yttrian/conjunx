from os import path, makedirs, getenv
import time

from aiohttp import web
from aiohttp_session import redis_storage, setup, get_session
from aioredis import create_pool

spool = '/var/spool/conjunx'

routes = web.RouteTableDef()

@routes.get('/')
async def hello(request):
    await get_session(request)

    return web.Response(text="Hello, world")

async def run():
    app = web.Application()
    app.add_routes(routes)

    redis = await create_pool((getenv('redis'), 6379))
    storage = redis_storage.RedisStorage(redis)
    setup(app, storage)

    makedirs(spool, exist_ok=True)

    return app