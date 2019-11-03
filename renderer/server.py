import shutil
import time
from os import path, makedirs

from aiohttp import web

from voicelines import Transcript, Collection

spool = '/var/spool/conjunx'

routes = web.RouteTableDef()


@routes.get('/')
async def hello(request):
    return web.Response(text="conjunx render server")


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


@routes.post('/transcript-test')
async def transcript_test(request):
    data = await request.post()

    transcript_loc = path.join(spool, str(time.time_ns()) + '.cjxt')

    with open(transcript_loc, 'w') as f:
        f.write(data['transcript'])

    t = Transcript(transcript_loc)
    c = Collection()

    c.add_transcript(t)
    d = c.speak(data['dictate'])

    return web.Response(text=str(d))


async def run():
    app = web.Application()
    app.add_routes(routes)

    shutil.rmtree(spool, ignore_errors=True)
    makedirs(spool)

    return app
