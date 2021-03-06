from utils.index import generate_random_string, get_playlist_duration, get_playlist_source, get_spotify_track_data,  get_youtube_track_data,  track_duration_ms
from models.index import GeneratePlaylist, GetPlaylist, Playlist
from ytmusicapi import YTMusic
import spotipy as sp
from spotipy.oauth2 import SpotifyClientCredentials
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

origins = os.getenv("CORS_ORIGINS").split(",")

# setup Spotify client
spotify_auth_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"), client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"))
spotify = sp.Spotify(auth_manager=spotify_auth_manager)

# setup Youtube client
ytmusic = YTMusic()

# FASTApi app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/get-playlist", response_model=Playlist)
async def get_playlist(data: GetPlaylist):
    playlist = {}
    playlist_data = get_playlist_source(data.url)
    if playlist_data is None:
        raise HTTPException(status_code=400, detail="playlist url is invalid")
    if playlist_data.source == 'YOUTUBE':
        try:
            gotten_playlist = ytmusic.get_playlist(
                playlist_data.playlist_id)
            tracks = []
            for track in gotten_playlist.get("tracks"):
                tracks.append(get_youtube_track_data(track))
            playlist = {
                "id": gotten_playlist.get('id'),
                "title":  gotten_playlist.get('title'),
                "description":  gotten_playlist.get('description'),
                "thumbnail": gotten_playlist.get('thumbnails')[0].get("url"),
                "author":  gotten_playlist.get('author').get("name"),
                "year":  gotten_playlist.get('year'),
                "duration":  gotten_playlist.get('duration'),
                "trackCount":  gotten_playlist.get('trackCount'),
                "tracks": tracks,
                "platform": "YOUTUBE",
            }
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"problem getting playlist - {e}")
    elif playlist_data.source == 'SPOTIFY':
        try:
            gotten_playlist = spotify.playlist(playlist_data.playlist_id)
            tracks = []
            total_duration = 0
            for tr in gotten_playlist.get("tracks").get("items"):
                track = tr.get("track")
                total_duration += track.get("duration_ms")
                tracks.append(get_spotify_track_data(track))
                pass

            playlist = {
                "id": gotten_playlist.get('id'),
                "title":  gotten_playlist.get('name'),
                "description":  gotten_playlist.get('description'),
                "thumbnail": gotten_playlist.get('images')[0].get("url"),
                "author":  gotten_playlist.get('owner').get("display_name"),
                "year":  "-",
                "duration":  get_playlist_duration(total_duration),
                "trackCount":  len(gotten_playlist.get("tracks").get("items")),
                "tracks": tracks,
                "platform": "SPOTIFY"
            }
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"problem getting playlist - {e}")
    return playlist


@app.post("/generate-playlist", response_model=Playlist)
async def generate_playlist(data: GeneratePlaylist):
    playlist = {}
    tracks = []
    total_duration = 0
    if data.platform == 'SPOTIFY':
        for q_track in data.tracks:
            artist = q_track.artists.split(",")[0].strip()
            query = f"artist:{artist} {q_track.title}"
            search_result = spotify.search(query)
            related_tracks = search_result.get("tracks").get("items")
            if len(related_tracks) > 0:
                track = get_spotify_track_data(
                    search_result.get("tracks").get("items")[0])
                total_duration += track_duration_ms(track.get("duration"))
                tracks.append(track)
    elif data.platform == 'YOUTUBE':
        for q_track in data.tracks:
            artist = q_track.artists.split(",")[0].strip()
            query = q_track.title + " " + artist
            search_result = ytmusic.search(query, "songs", limit=1)
            if len(search_result) > 0:
                track = get_youtube_track_data(search_result[0])
                total_duration += track_duration_ms(track.get("duration"))
                tracks.append(track)
    else:
        raise HTTPException(
            status_code=400, detail=f"Invalid data source")
    playlist = {
        "id": generate_random_string(10),
        "title":  "NEW PLAYLIST",
        "description":  "Playlist generated by Hoodini(damiisdandy)",
        "thumbnail": data.thumbnail,
        "author":  "You",
        "year": str(datetime.now().date().strftime("%Y")),
        "duration":  get_playlist_duration(total_duration),
        "trackCount":  len(tracks),
        "tracks": tracks,
        "similarity": 0,
        "platform": data.platform,
    }
    return playlist
