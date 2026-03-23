from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
import uuid


def _new_id() -> str:
    return str(uuid.uuid4())


def _today() -> str:
    return date.today().isoformat()


@dataclass
class Song:
    title: str
    artist: str
    duration_ms: int
    file_path: str
    id: str = field(default_factory=_new_id)
    date_added: str = field(default_factory=_today)

    def duration_str(self) -> str:
        total_seconds = self.duration_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"


@dataclass
class Playlist:
    name: str
    id: str = field(default_factory=_new_id)
    cover_art_path: str | None = None
    songs: list[Song] = field(default_factory=list)

    def total_duration_str(self) -> str:
        total_ms = sum(s.duration_ms for s in self.songs)
        total_seconds = total_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours}h {minutes}m"
        return f"{minutes}m {seconds}s"
