from utils.index import get_playlist_duration, get_playlist_source, get_track_duration
from models.index import GetPlaylist, Playlist
from ytmusicapi import YTMusic
import spotipy as sp
from spotipy.oauth2 import SpotifyClientCredentials
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv


load_dotenv()

origins = [
    "http://localhost:3000",
    "https://playlist-converter.vercel.app",
    'https://hoodini.damiisdandy.com'
]

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
                artists = ""
                for artist in track.get("artists"):
                    if track.get("artists")[-1].get("name") != artist.get("name"):
                        artists += (artist.get("name") + ", ")
                    else:
                        artists += artist.get("name")
                tracks.append({
                    "title": track.get("title"),
                    "url": "https://music.youtube.com/watch?v=" + track.get("videoId"),
                    "artists": artists,
                    "duration": track.get("duration"),
                    "thumbnail": track.get("thumbnails")[0].get("url"),
                    "album": track.get("album").get("name") if track.get("album") is not None else "",
                    "isExplicit": track.get("isExplicit"),
                    "searchKey": track.get("title") + " " + track.get("album").get("name") if track.get("album") is not None else ""
                })
            playlist = {
                "id": gotten_playlist.get('id'),
                "title":  gotten_playlist.get('title'),
                "description":  gotten_playlist.get('description'),
                "thumbnail": gotten_playlist.get('thumbnails')[0].get("url"),
                "author":  gotten_playlist.get('author').get("name"),
                "year":  gotten_playlist.get('year'),
                "duration":  gotten_playlist.get('duration'),
                "trackCount":  gotten_playlist.get('trackCount'),
                "tracks": tracks
            }
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"problem getting playlist - {e}")
    elif playlist_data.source == 'SPOTIFY':
        try:
            gotten_playlist = spotify.playlist(playlist_data.playlist_id)
            tracks = []
            total_duration = 0
            print(gotten_playlist.get("tracks").get(
                "items")[0].get("track").get("href"))
            for tr in gotten_playlist.get("tracks").get("items"):
                track = tr.get("track")
                artists = ""
                total_duration += track.get("duration_ms")
                for artist in track.get("artists"):
                    if track.get("artists")[-1].get("name") != artist.get("name"):
                        artists += (artist.get("name") + ", ")
                    else:
                        artists += artist.get("name")
                tracks.append({
                    "title": track.get("name"),
                    "url": "https://open.spotify.com/track/" + track.get("href").split("/")[-1],
                    "artists": artists,
                    "duration": get_track_duration(track.get("duration_ms")),
                    "thumbnail": track.get("album").get("images")[0].get("url"),
                    "album": track.get("album").get("name"),
                    "isExplicit": track.get("explicit"),
                    "searchKey": track.get("name") + " " + track.get("album").get("name")
                })
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
                "tracks": tracks
            }
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"problem getting playlist - {e}")
    elif playlist_data.source == 'APPLE':
        pass
    return playlist
