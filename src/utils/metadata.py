from __future__ import annotations
from pathlib import Path

from data.models import Song


class MetadataReader:
    @staticmethod
    def read(file_path: str) -> Song:
        path = Path(file_path)
        ext = path.suffix.lower()

        title = path.stem
        artist = "Unknown Artist"
        duration_ms = 0

        try:
            if ext == ".mp3":
                duration_ms, title, artist = MetadataReader._read_mp3(path, title, artist)
            elif ext == ".wav":
                duration_ms, title, artist = MetadataReader._read_wav(path, title, artist)
        except Exception:
            pass

        return Song(
            title=title,
            artist=artist,
            duration_ms=duration_ms,
            file_path=str(path.resolve()),
        )

    @staticmethod
    def _read_mp3(path: Path, default_title: str, default_artist: str) -> tuple[int, str, str]:
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3, TIT2, TPE1

        audio = MP3(str(path))
        duration_ms = int(audio.info.length * 1000)

        title = default_title
        artist = default_artist
        try:
            tags = ID3(str(path))
            if "TIT2" in tags:
                title = str(tags["TIT2"]) or default_title
            if "TPE1" in tags:
                artist = str(tags["TPE1"]) or default_artist
        except Exception:
            pass

        return duration_ms, title, artist

    @staticmethod
    def _read_wav(path: Path, default_title: str, default_artist: str) -> tuple[int, str, str]:
        from mutagen.wave import WAVE

        audio = WAVE(str(path))
        duration_ms = int(audio.info.length * 1000)

        title = default_title
        artist = default_artist
        try:
            if audio.tags:
                if "TIT2" in audio.tags:
                    title = str(audio.tags["TIT2"]) or default_title
                if "TPE1" in audio.tags:
                    artist = str(audio.tags["TPE1"]) or default_artist
        except Exception:
            pass

        return duration_ms, title, artist
