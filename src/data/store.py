from __future__ import annotations
import json
import os
from pathlib import Path
from data.models import Playlist, Song

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_FILE = BASE_DIR / "data" / "playlists.json"


class DataStore:
    def __init__(self) -> None:
        self._playlists: list[Playlist] = []
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.load()

    def load(self) -> None:
        if not DATA_FILE.exists():
            self._playlists = []
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self._playlists = [self._deserialize_playlist(p) for p in raw.get("playlists", [])]
        except (json.JSONDecodeError, KeyError):
            self._playlists = []

    def save(self) -> None:
        tmp = DATA_FILE.with_suffix(".json.tmp")
        data = {
            "version": 1,
            "playlists": [self._serialize_playlist(p) for p in self._playlists],
        }
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, DATA_FILE)

    def get_playlists(self) -> list[Playlist]:
        return list(self._playlists)

    def add_playlist(self, playlist: Playlist) -> None:
        self._playlists.append(playlist)
        self.save()

    def update_playlist(self, playlist: Playlist) -> None:
        for i, p in enumerate(self._playlists):
            if p.id == playlist.id:
                self._playlists[i] = playlist
                break
        self.save()

    def delete_playlist(self, playlist_id: str) -> None:
        self._playlists = [p for p in self._playlists if p.id != playlist_id]
        self.save()

    def is_file_referenced(self, file_path: str) -> bool:
        target = Path(file_path).resolve()
        for playlist in self._playlists:
            for song in playlist.songs:
                if Path(song.file_path).resolve() == target:
                    return True
        return False

    @staticmethod
    def _serialize_playlist(p: Playlist) -> dict:
        return {
            "id": p.id,
            "name": p.name,
            "cover_art_path": p.cover_art_path,
            "songs": [
                {
                    "id": s.id,
                    "title": s.title,
                    "artist": s.artist,
                    "duration_ms": s.duration_ms,
                    "file_path": s.file_path,
                    "date_added": s.date_added,
                }
                for s in p.songs
            ],
        }

    @staticmethod
    def _deserialize_playlist(data: dict) -> Playlist:
        songs = [
            Song(
                id=s["id"],
                title=s["title"],
                artist=s.get("artist", "Unknown Artist"),
                duration_ms=s["duration_ms"],
                file_path=s["file_path"],
                date_added=s.get("date_added", ""),
            )
            for s in data.get("songs", [])
        ]
        return Playlist(
            id=data["id"],
            name=data["name"],
            cover_art_path=data.get("cover_art_path"),
            songs=songs,
        )
