#  render.py
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

import time
from os import path, listdir
from zipfile import ZipFile

from moviepy.editor import VideoFileClip, concatenate_videoclips

from voicelines import VoiceLine, Collection, Transcript

spool = '/var/spool/conjunx'


class RenderJob:
    __slots__ = ['id', 'lines']

    def __init__(self, cjxa_loc, dictate: str):
        self.id = str(time.time_ns())
        self.lines = self.unpack_cjxa(cjxa_loc, dictate)

    def make_clip(self, voice_line: VoiceLine):
        start, end = voice_line.timestamps
        video_loc = path.join(spool, self.id, voice_line.video)

        return VideoFileClip(video_loc).subclip(start, end)

    def render(self):
        movie = concatenate_videoclips([self.make_clip(voice_line) for voice_line in self.lines])

        video_loc = path.join(spool, self.id + '.mp4')
        movie.write_videofile(video_loc)

        return video_loc

    def unpack_cjxa(self, archive_loc, dictate: str):
        project_loc = path.join(spool, self.id)

        with ZipFile(archive_loc, 'r') as z:
            z.extractall(project_loc)

        c = Collection()

        transcripts = [f for f in listdir(project_loc) if f.endswith('.cjxt')]

        for transcript in transcripts:
            transcript_loc = path.join(project_loc, transcript)

            with open(transcript_loc, 'r') as f:
                t = Transcript(transcript_loc)
                c.add_transcript(t)

        return c.speak(dictate)
