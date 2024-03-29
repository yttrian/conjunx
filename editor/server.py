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
from os import makedirs, getenv

from aiohttp import web
from aiohttp_session import redis_storage, setup, new_session, get_session
from aioredis import create_pool

from cjxproject import CJXProject

spool = '/var/spool/conjunx'

routes = web.RouteTableDef()
projects = {}


# The user facing editor

@routes.get('/')
async def editor(request):
    session = await get_session(request)

    if session.identity is None:
        session = await new_session(request)

    session['last_visited'] = time.time()
    get_project(session)

    return web.FileResponse('./static/fallback.html')


def get_project(session):
    sid = session.identity
    if sid not in projects:
        projects[sid] = CJXProject()

    return projects[sid]


# Clip/transcript related endpoints

@routes.get('/clip')
async def get_clips_list(request):
    session = await get_session(request)
    project = get_project(session)

    return web.json_response(project.get_clips_list())


@routes.post('/clip')
async def upload_clip(request):
    session = await get_session(request)
    project = get_project(session)

    reader = await request.multipart()

    field = await reader.next()
    assert field.name == 'data'

    clip_id = await project.add_clip(field)

    return web.Response(text=clip_id)


@routes.delete('/clip/{id}')
async def delete_clip(request):
    session = await get_session(request)
    project = get_project(session)

    clip_id = request.match_info['id']
    if project.delete_clip(clip_id):
        return web.HTTPOk()

    return web.HTTPNotFound()


@routes.get('/clip/{id}')
async def get_clip(request):
    session = await get_session(request)
    project = get_project(session)

    clip_id = request.match_info['id']
    clip = project.get_clip(clip_id)

    if clip is not None:
        headers = {'Content-Type': 'video/mp4'}
        return web.FileResponse(clip, headers=headers)

    return web.HTTPNotFound()


@routes.get('/clip/{id}/transcript')
async def get_transcript(request):
    session = await get_session(request)
    project = get_project(session)

    clip_id = request.match_info['id']
    transcript = project.get_transcript(clip_id)

    if transcript is None:
        return web.HTTPNotFound()

    return web.Response(text=transcript)


@routes.put('/clip/{id}/transcript')
async def update_transcript(request):
    return web.HTTPNotImplemented()


# .cjxa archive related endpoints

@routes.get('/archive')
async def download_archive(request):
    session = await get_session(request)
    project = get_project(session)

    return web.FileResponse(project.create_archive())


@routes.post('/archive')  # was put but fallback.html wants post
async def upload_archive(request):
    session = await get_session(request)
    project = get_project(session)

    reader = await request.multipart()

    field = await reader.next()
    assert field.name == 'data'

    await project.load_archive(field)

    return web.HTTPOk()


# Render related endpoints

@routes.post('/render')
async def render(request):
    session = await get_session(request)
    project = get_project(session)

    data = await request.post()
    dictate = data['dictate']

    headers = {'Content-Disposition': 'Attachment'}

    return web.FileResponse(await project.render(dictate), headers=headers)


# Gunicorn app builder

async def run():
    app = web.Application()
    routes.static('/', './static')
    app.add_routes(routes)

    redis = await create_pool((getenv('redis'), 6379))
    storage = redis_storage.RedisStorage(redis)
    setup(app, storage)

    shutil.rmtree(spool, ignore_errors=True)
    makedirs(spool)

    return app
