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

    project = get_project(session)

    return web.Response(text=f"Hello, {session.identity}")


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


@routes.put('/archive')
async def upload_archive(request):
    session = await get_session(request)
    project = get_project(session)

    reader = await request.multipart()

    field = await reader.next()
    assert field.name == 'data'

    await project.load_archive(field)

    return web.HTTPOk()


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

    shutil.rmtree(spool, ignore_errors=True)
    makedirs(spool)

    return app
