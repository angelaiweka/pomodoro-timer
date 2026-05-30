import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = "http://127.0.0.1:8888/callback"

def create_spotify_client():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope="user-modify-playback-state user-read-playback-state playlist-read-private"
    ))
    return sp

def get_playlists(sp):
    results = sp.current_user_playlists()
    playlists = [(item['name'], item['uri']) for item in results['items']]
    return playlists

def play_playlist(sp, playlist_uri):
    try:
        sp.start_playback(context_uri=playlist_uri)
    except Exception as e:
        print(f"Playback error: {e}")

def pause_music(sp):
    try:
        sp.pause_playback()
    except Exception as e:
        print(f"Pause error: {e}")

def resume_music(sp):
    try:
        sp.start_playback()
    except Exception as e:
        print(f"Resume error: {e}")