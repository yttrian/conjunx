#  server.py
#
#  conjunx, an automated TTS tool for tagged source videos
#
#  Copyright (C) 2019 by Ian Moore
#
#  This file is part of conjunx.
#
#  conjunx is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of
#  the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import shutil
import time
from os import path, makedirs

from aiohttp import web

from render import RenderJob

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
    dictate = await field.text()

    # Get the data files
    field = await reader.next()
    assert field.name == 'data'

    filename = str(time.time_ns()) + '.cjxa'
    archive_loc = path.join(spool, filename)

    with open(archive_loc, 'wb') as f:
        while True:
            chunk = await field.read_chunk()  # 8192 bytes by default.
            if not chunk:
                break
            f.write(chunk)

    try:
        job = RenderJob(archive_loc, dictate)
        movie = job.render()

        return web.FileResponse(movie)
    except IndexError:
        return web.HTTPBadRequest(text="Needed words not available!")


async def run():
    app = web.Application()
    app.add_routes(routes)

    shutil.rmtree(spool, ignore_errors=True)
    makedirs(spool)

    return app
