from typing import List

from redis import Redis
from utils.url_parser import get_playlist_source
from utils.parse_track import parse_spotify_track_data, parse_youtube_track_data
from models.index import GeneratePlaylist, GetPlaylist, Playlist, PlaylistSource, Track
from ytmusicapi import YTMusic
import spotipy as sp
from spotipy.oauth2 import SpotifyClientCredentials
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from config.db import create_redis
import os
import json


SONG_CACHE_EXPIRY = 24 * 60 * 60  # 24 hours in seconds (TTL)

load_dotenv()

# CORS
cors_origins_str = os.getenv("CORS_ORIGINS")
origins = cors_origins_str.split() if cors_origins_str else []


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

# TEST LINK: https://open.spotify.com/playlist/6Q85Qap1zdgxGMRSjMh2Pb?si=313b271be54943f0
# https://music.youtube.com/playlist?list=PLDInZaOOyBblfcPmlPBzfKH-tyDwUWOYJ


@app.get("/")
async def index():
    return {"message": "Application is running :)"}


@app.post("/get-playlist", response_model=Playlist)
async def get_playlist(data: GetPlaylist, cache: Redis = Depends(create_redis)) -> Playlist:
    playlist_info = get_playlist_source(data.url)
    if playlist_info is None:
        raise HTTPException(status_code=400, detail="playlist url is invalid")

    match playlist_info.source:
        case PlaylistSource.SPOTIFY:
            try:
                spotify_playlist = spotify.playlist(
                    playlist_id=playlist_info.playlist_id)
            except sp.exceptions.SpotifyException:
                raise HTTPException(
                    status_code=404, detail="spotify playlist does not exist")
            if spotify_playlist is None:
                raise HTTPException(
                    status_code=400, detail="problem fetching spotify playlist")
            tracks = spotify_playlist.get("tracks").get("items")
            parsed_tracks: List[Track] = []
            duration = 0

            for track in tracks:
                song = track.get("track")
                if song is not None:
                    parsed_song = parse_spotify_track_data(song)
                    duration += parsed_song.duration
                    parsed_tracks.append(parsed_song)
                    song_exists = cache.exists(parsed_song.id)
                    if not song_exists:
                        cache.setex(name=parsed_song.id,
                                    time=SONG_CACHE_EXPIRY,
                                    value=parsed_song.model_dump_json())

            return Playlist(
                id=spotify_playlist.get('id'),
                title=spotify_playlist.get('name'),
                description=spotify_playlist.get('description'),
                thumbnail=spotify_playlist.get('images')[0].get("url"),
                author=spotify_playlist.get('owner').get("display_name"),
                duration=duration,
                track_count=spotify_playlist.get("tracks").get("total"),
                tracks=parsed_tracks,
                platform=PlaylistSource.SPOTIFY,
                similarity=0,
            )

        case PlaylistSource.YOUTUBE:
            try:
                youtube_playlist = ytmusic.get_playlist(
                    playlistId=playlist_info.playlist_id)
            except Exception:
                raise HTTPException(
                    status_code=404, detail="youtube playlist does not exist")
            if youtube_playlist is None:
                raise HTTPException(
                    status_code=400, detail="problem fetching youtube playlist")

            tracks = youtube_playlist.get("tracks")
            parsed_tracks: List[Track] = []
            if tracks:
                for track in tracks:
                    parsed_song = parse_youtube_track_data(track)
                    parsed_tracks.append(parsed_song)
                    song_exists = cache.exists(parsed_song.id)
                    if not song_exists:
                        cache.setex(name=parsed_song.id,
                                    time=SONG_CACHE_EXPIRY,
                                    value=parsed_song.model_dump_json())

            thumbnails = youtube_playlist.get("thumbnails") or [{"url": ""}]
            author = youtube_playlist.get("author") or {"name": ""}

            return Playlist(
                id=youtube_playlist.get('id') or "",
                title=youtube_playlist.get('title') or "",
                description=youtube_playlist.get('description') or "",
                thumbnail=thumbnails[0].get("url"),
                author=author.get("name") or "",
                duration=(youtube_playlist.get(
                    'duration_seconds') or 0) * 1000,
                track_count=youtube_playlist.get('trackCount') or 0,
                tracks=parsed_tracks,
                platform=PlaylistSource.YOUTUBE,
                similarity=0,
            )
    raise HTTPException(
        status_code=500, detail="Internal server error")


@app.post("/generate-playlist", response_model=Playlist)
async def generate_playlist(data: GeneratePlaylist) -> Playlist:
    platform = data.platform
    redis_key = data.playlist_redis_key

    # fetch array of tracks from redis

    # loop through tracks and search

    # return new tracks and similarity score

    return Playlist(
        id="",
        title="",
        description="",
        thumbnail="",
        author="",
        duration=0,
        track_count=0,
        tracks=[],
        platform=PlaylistSource.YOUTUBE,
        similarity=0,
    )
    # playlist = {}
    # tracks = []
    # total_duration = 0
    # if data.platform == 'SPOTIFY':
    #     for q_track in data.tracks:
    #         artist = q_track.artists.split(",")[0].strip()
    #         query = f"artist:{artist} {q_track.title}"
    #         search_result = spotify.search(query)
    #         related_tracks = search_result.get("tracks").get("items")
    #         if len(related_tracks) > 0:
    #             track = parse_spotify_track_data(
    #                 search_result.get("tracks").get("items")[0])
    #             total_duration += track_duration_ms(track.get("duration"))
    #             tracks.append(track)
    # elif data.platform == 'YOUTUBE':
    #     for q_track in data.tracks:
    #         artist = q_track.artists.split(",")[0].strip()
    #         query = q_track.title + " " + artist
    #         search_result = ytmusic.search(query, "songs", limit=1)
    #         if len(search_result) > 0:
    #             track = get_youtube_track_data(search_result[0])
    #             total_duration += track_duration_ms(track.get("duration"))
    #             tracks.append(track)
    # else:
    #     raise HTTPException(
    #         status_code=400, detail=f"Invalid data source")
    # playlist = {
    #     "id": generate_random_string(10),
    #     "title":  "NEW PLAYLIST",
    #     "description":  "Playlist generated by Hoodini(damiisdandy)",
    #     "thumbnail": data.thumbnail,
    #     "author":  "You",
    #     "year": str(datetime.now().date().strftime("%Y")),
    #     "duration":  get_playlist_duration(total_duration),
    #     "trackCount":  len(tracks),
    #     "tracks": tracks,
    #     "similarity": 0,
    #     "platform": data.platform,
    # }
    # return playlist
