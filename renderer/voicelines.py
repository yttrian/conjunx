import csv
import itertools
from typing import Dict, List, Tuple


class VoiceLine:
    __slots__ = ['speech', 'video', 'timestamps', 'next']

    def __init__(self, speech: str, video, timestamps: (float, float), nxt: 'VoiceLine' = None):
        self.speech = speech
        self.video = video
        self.timestamps = timestamps
        self.next = nxt

    def __str__(self):
        return f"VoiceLine({self.speech} from {self.timestamps[0]}s to {self.timestamps[1]} -> {self.next})"


class Transcript:
    __slots__ = ['lines']

    def __init__(self, file):
        self.lines = self.parse_lines(file)

    @staticmethod
    def parse_lines(file) -> Dict[str, List[VoiceLine]]:
        with open(file, 'r') as f:
            r = csv.reader(f)

            video = next(r)[0]

            lines = [VoiceLine(l[0], video, (l[1], l[2])) for l in r]
            tagged_lines = {}

            for i in range(len(lines)):
                line = lines[i]
                speech = line.speech

                try:
                    line.next = lines[i + 1]
                except IndexError:
                    pass

                if speech not in tagged_lines:
                    tagged_lines[speech] = [line]
                else:
                    tagged_lines[speech].append(line)

        return tagged_lines

    def __str__(self):
        lines = [str(line) for line in itertools.chain.from_iterable(self.lines.values())]
        return f"Transcript({lines})"


class Collection:
    __slots__ = ['transcripts']

    def __init__(self):
        self.transcripts = {}

    def add_transcript(self, transcript: Transcript):
        for (k, v) in transcript.lines.items():
            if k in self.transcripts:
                self.transcripts[k] += v
            else:
                self.transcripts[k] = v

    def speak(self, dictate: str):
        """
        Strings together a list of VoiceLines based on a given input, any missing word is a fatal error!
        :param dictate: what to try to say
        :return: the list of voice lines to used in video editing
        """
        words = dictate.split(" ")
        lines = []

        def choose_best_voice_line(remaining_text: List[str], voice_lines: List[VoiceLine]) -> VoiceLine:
            def score(voice_line: VoiceLine, text: List[str]) -> int:
                if voice_line is not None and voice_line.speech == text[0]:
                    return score(voice_line.next, text[1:]) + 1
                return 0

            return max(voice_lines, key=lambda x: score(x, remaining_text))

        i = 0
        while i < len(words):
            def growing_search(start: int, end: int) -> Tuple[VoiceLine, int]:
                term = " ".join(words[start:end])
                voice_line = self.transcripts.get(term)

                if voice_line is None:
                    growing_search(start, end + 1)
                else:
                    return voice_line, end

            line, end = growing_search(i, i + 1)
            lines.append(line)

            i = end

        return lines
