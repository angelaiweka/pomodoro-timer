import json
import threading
import subprocess
import platform
import requests

_player_process = None
_current_stream_url = None

GENRE_TAGS = [
    "lofi",
    "lofi hip hop",
    "japanese",
    "j-pop",
    "anime",
    "chillout",
    "instrumental",
    "piano",
    "classical",
    "ambient",
    "cafe",
    "jazz",
]

SERVERS = [
    "de1.api.radio-browser.info",
    "nl1.api.radio-browser.info",
    "at1.api.radio-browser.info",
]

HEADERS = {
    "User-Agent": "PomodoroTimer/1.0",
    "Accept": "application/json",
}

def search_stations(tag, limit=15):
    """Search Radio Browser API for stations by tag. Returns list of (name, url) tuples."""
    params = {
        "tag": tag,
        "limit": limit,
        "hidebroken": "true",
        "order": "votes",
        "reverse": "true",
    }
    for server in SERVERS:
        try:
            url = f"https://{server}/json/stations/search"
            resp = requests.get(url, params=params, headers=HEADERS, timeout=8)
            resp.raise_for_status()
            data = resp.json()
            stations = [
                (s["name"].strip(), s["url_resolved"] or s["url"])
                for s in data
                if (s.get("url_resolved") or s.get("url"))
            ]
            if stations:
                return stations
        except Exception as e:
            print(f"Radio Browser error ({server}): {e}")
            continue
    return []

def play_station(stream_url):
    """Play a radio stream using ffplay (comes with ffmpeg)."""
    global _player_process, _current_stream_url
    stop_station()
    _current_stream_url = stream_url

    def _play():
        global _player_process
        try:
            flags = {}
            if platform.system() == "Windows":
                flags["creationflags"] = subprocess.CREATE_NO_WINDOW
            _player_process = subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", stream_url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **flags,
            )
        except FileNotFoundError:
            print("ffplay not found. Install ffmpeg: brew install ffmpeg")

    threading.Thread(target=_play, daemon=True).start()

def stop_station():
    """Stop the currently playing station."""
    global _player_process
    if _player_process and _player_process.poll() is None:
        _player_process.terminate()
        _player_process = None

def is_playing():
    return _player_process is not None and _player_process.poll() is None