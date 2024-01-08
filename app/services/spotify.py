import os
import spotipy as sp
from spotipy.oauth2 import SpotifyClientCredentials

spotify_auth_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
)
spotify = sp.Spotify(auth_manager=spotify_auth_manager)

SpotifyException = sp.exceptions.SpotifyException
