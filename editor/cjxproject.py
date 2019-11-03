import shutil
import time
import uuid
from os import path, makedirs, remove, listdir
from zipfile import ZipFile, ZIP_STORED

spool = '/var/spool/conjunx'


class CJXProject:
    __slots__ = ['id', 'clips']

    def __init__(self):
        self.id = str(time.time_ns())
        self.clips = {}

        makedirs(path.join(spool, self.id))  # storage location

    def create_archive(self):
        archive_loc = path.join(spool, self.id + '.cjxa')

        with ZipFile(archive_loc, 'w', compression=ZIP_STORED) as z:
            for clip in self.clips.values():
                z.write(clip.transcript_loc, path.basename(clip.transcript_loc))
                z.write(clip.video_loc, path.basename(clip.video_loc))

        return archive_loc

    async def load_archive(self, field):
        project_loc = path.join(spool, self.id)
        archive_loc = project_loc + '.cjxa'

        shutil.rmtree(spool, ignore_errors=True)  # clear current contents
        makedirs(project_loc)  # storage location
        self.clips.clear()  # clear clips listing

        await retrieve_file(field, archive_loc)

        with ZipFile(archive_loc, 'r') as z:
            z.extractall(project_loc)

        transcripts = [f for f in listdir(project_loc) if f.endswith('.cjxt')]

        for transcript in transcripts:
            transcript_loc = path.join(spool, self.id, transcript)

            with open(transcript_loc, 'r') as f:
                full_filename = f.readline()
                filename = full_filename.split('.')[0]
                video_loc = path.join(spool, self.id, filename + '.cjxv')

            clip_id = str(uuid.uuid4())
            clip = Clip(filename, video_loc, transcript_loc)

            self.clips[clip_id] = clip

    async def add_clip(self, field):
        """
        :param field: the multipart field holding the clip
        :return: the clip id
        """
        filename = field.filename.split(".")[0]
        video_loc = path.join(spool, self.id, filename + '.cjxv')
        transcript_loc = path.join(spool, self.id, filename + '.cjxt')

        await retrieve_file(field, video_loc)

        with open(transcript_loc, 'w') as f:
            f.writelines(filename + '.cjxv')

        clip_id = str(uuid.uuid4())
        clip = Clip(filename, video_loc, transcript_loc)

        self.clips[clip_id] = clip

        return clip_id

    def get_clips_list(self):
        """
        :return: a list of clips with their ids and names
        """
        return {clip_id: c.name for (clip_id, c) in zip(self.clips.keys(), self.clips.values())}

    def delete_clip(self, clip_id):
        """
        Deletes the requested clip and associated transcript.
        :param clip_id: id of the clip
        :return: True if it succeeded, and False if it fails
        """
        if clip_id not in self.clips:
            return False

        self.clips.pop(clip_id).delete()

        return True

    def get_transcript(self, clip_id):
        """
        Gets the transcript from a clip
        :param clip_id: id of the clip
        :return: transcript if clip exists otherwise None
        """
        if clip_id not in self.clips:
            return None

        clip = self.clips[clip_id]

        return clip.get_transcript()


class Clip:
    __slots__ = ['name', 'video_loc', 'transcript_loc']

    def __init__(self, name, video_loc, transcript_loc):
        self.name = name
        self.video_loc = video_loc
        self.transcript_loc = transcript_loc

    def delete(self):
        remove(self.video_loc)
        remove(self.transcript_loc)

    def get_transcript(self):
        with open(self.transcript_loc, 'r') as f:
            data = "".join(f.readlines()[1:])

        return data


async def retrieve_file(field, destination):
    with open(destination, 'wb') as f:
        while True:
            chunk = await field.read_chunk()  # 8192 bytes by default.
            if not chunk:
                break
            f.write(chunk)
