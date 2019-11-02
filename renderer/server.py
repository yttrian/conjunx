from os import path, mkdir
import time

from aiohttp import web

spool = '/var/spool/conjunx'

routes = web.RouteTableDef()

@routes.get('/')
async def hello(request):
    return web.Response(text="Hello, world")

@routes.post('/render')
async def render(request):
    # https://aiohttp.readthedocs.io/en/stable/web_quickstart.html#file-uploads
    reader = await request.multipart()

    # Get the requested text to convert
    field = await reader.next()
    assert field.name == 'dictate'
    dictate = await field.read(decode=True)

    # Get the data files
    field = await reader.next()
    assert field.name == 'data'

    filename = str(time.time_ns()) + '.cjx'

    with open(path.join(spool, filename), 'wb') as f:
        while True:
            chunk = await field.read_chunk()  # 8192 bytes by default.
            if not chunk:
                break
            f.write(chunk)

    return web.HTTPOk()

async def run():
    app = web.Application()
    app.add_routes(routes)

    mkdir(spool)

    return app