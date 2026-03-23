# Music Player

A Spotify-inspired desktop music player built with Python and PyQt6. Manage playlists, play local audio files, and control playback — all from a clean dark-themed UI.

## Features

- **Playlists** — create named playlists with custom cover art
- **Local audio** — add MP3 and WAV files from anywhere on your machine; files are copied to a local `music/` folder
- **Playback controls** — play, pause, skip, seek, and adjust volume
- **Shuffle & Loop** — toggle shuffle and loop modes from the player bar
- **Queue** — view and manage the upcoming play order; drag to reorder, right-click to remove
- **Right-click menus** — play, add to queue, or remove songs; delete playlists from the sidebar
- **Cover art** — upload any image as playlist art; click existing art to replace it
- **Persistent storage** — playlists and metadata are saved to `data.json` automatically

## Requirements

- **Python 3.10+**
- **VLC Media Player (64-bit)** — [download from videolan.org](https://www.videolan.org/vlc/)
- Python packages listed in `requirements.txt`

> **Important:** VLC must be the 64-bit version to match a 64-bit Python installation.

## Installation

```bash
# 1. Install 64-bit VLC from https://www.videolan.org/vlc/

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run the app
python src/main.py
```

## Project Structure

```
music-player/
├── src/
│   ├── main.py              # Entry point
│   ├── audio/
│   │   └── player.py        # VLC-based audio engine
│   ├── data/
│   │   ├── models.py        # Song and Playlist dataclasses
│   │   └── store.py         # JSON persistence
│   ├── ui/
│   │   ├── main_window.py   # Central signal router
│   │   ├── sidebar.py       # Playlist list panel
│   │   ├── song_list.py     # Song table and playlist header
│   │   ├── player_bar.py    # Playback controls bar
│   │   ├── queue_panel.py   # Queue side panel
│   │   ├── playlist_dialog.py  # New playlist dialog
│   │   └── theme.py         # QSS dark theme stylesheet
│   └── utils/
│       ├── metadata.py      # Song metadata extraction (mutagen)
│       └── image_utils.py   # Cover art scaling utility
├── assets/
│   └── icons/
│       └── app_icon.svg
├── music/                   # Local audio files (gitignored)
├── data.json                # Playlist data (auto-generated)
└── requirements.txt
```
