from os import path, makedirs, getenv
import time

from aiohttp import web
from aiohttp_session import redis_storage, setup, get_session
from aioredis import create_pool

spool = '/var/spool/conjunx'

routes = web.RouteTableDef()

# The user facing editor

@routes.get('/')
async def hello(request):
    await get_session(request)

    return web.Response(text="Hello, world")

# Clip/transcript related endpoints

@routes.post('/clip/')
async def upload_clip(request):
    return web.HTTPNotImplemented()

@routes.delete('/clip/{id}')
async def delete_clip(request):
    return web.HTTPNotImplemented()

@routes.patch('/clip/{id}/transcript')
async def update_transcript(request):
    return web.HTTPNotImplemented()

# .cjxa archive related endpoints

@routes.get('/archive')
async def download_archive(request):
    return web.HTTPNotImplemented()

@routes.put('/archive')
async def upload_archive(request):
    return web.HTTPNotImplemented()

# Render related endpoints

@routes.get('/render')
async def render(request):
    return web.HTTPNotImplemented()

# Gunicorn app builder

async def run():
    app = web.Application()
    app.add_routes(routes)

    redis = await create_pool((getenv('redis'), 6379))
    storage = redis_storage.RedisStorage(redis)
    setup(app, storage)

    makedirs(spool, exist_ok=True)

    return app