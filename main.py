from typing import List, Optional
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
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
)
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


@app.get("/")
async def index():
    return {"message": "Application is running :)"}


@app.post("/get-playlist", response_model=Playlist)
async def get_playlist(data: GetPlaylist) -> Playlist:
    playlist_info = get_playlist_source(data.url)
    if playlist_info is None:
        raise HTTPException(status_code=400, detail="playlist url is invalid")

    match playlist_info.source:
        case PlaylistSource.SPOTIFY:
            try:
                spotify_playlist = spotify.playlist(
                    playlist_id=playlist_info.playlist_id
                )
            except sp.exceptions.SpotifyException:
                raise HTTPException(
                    status_code=404, detail="spotify playlist does not exist"
                )
            if spotify_playlist is None:
                raise HTTPException(
                    status_code=400, detail="problem fetching spotify playlist"
                )
            tracks = spotify_playlist.get("tracks").get("items")
            parsed_tracks: List[Track] = []
            duration = 0

            for track in tracks:
                song = track.get("track")
                if song is not None:
                    parsed_song = parse_spotify_track_data(song)
                    duration += parsed_song.duration
                    parsed_tracks.append(parsed_song)

            return Playlist(
                id=spotify_playlist.get("id"),
                title=spotify_playlist.get("name"),
                description=spotify_playlist.get("description"),
                thumbnail=spotify_playlist.get("images")[0].get("url"),
                author=spotify_playlist.get("owner").get("display_name"),
                duration=duration,
                track_count=spotify_playlist.get("tracks").get("total"),
                tracks=parsed_tracks,
                platform=PlaylistSource.SPOTIFY,
                similarity=0,
            )

        case PlaylistSource.YOUTUBE:
            try:
                youtube_playlist = ytmusic.get_playlist(
                    playlistId=playlist_info.playlist_id
                )
            except Exception:
                raise HTTPException(
                    status_code=404, detail="youtube playlist does not exist"
                )
            if youtube_playlist is None:
                raise HTTPException(
                    status_code=400, detail="problem fetching youtube playlist"
                )

            tracks = youtube_playlist.get("tracks")
            parsed_tracks: List[Track] = []

            if tracks:
                for track in tracks:
                    parsed_song = parse_youtube_track_data(track)
                    parsed_tracks.append(parsed_song)

            thumbnails = youtube_playlist.get("thumbnails") or [{"url": ""}]
            author = youtube_playlist.get("author") or {"name": ""}

            return Playlist(
                id=youtube_playlist.get("id") or "",
                title=youtube_playlist.get("title") or "",
                description=youtube_playlist.get("description") or "",
                thumbnail=thumbnails[0].get("url"),
                author=author.get("name") or "",
                duration=(youtube_playlist.get(
                    "duration_seconds") or 0) * 1000,
                track_count=youtube_playlist.get("trackCount") or 0,
                tracks=parsed_tracks,
                platform=PlaylistSource.YOUTUBE,
                similarity=0,
            )
    raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/generate-playlist", response_model=Playlist)
async def generate_playlist(data: GeneratePlaylist, cache: Redis = Depends(create_redis)) -> Playlist:
    platform = data.platform

    tracks: List[Track] = []
    total_duration = 0
    track_count = 0

    match platform:
        case PlaylistSource.SPOTIFY:
            for query in data.search_queries:
                track: Optional[Track] = None

                cached_song = cache.get(query)
                if cached_song is not None:
                    track_json = json.loads(cached_song)  # type: ignore
                    track = Track(**track_json)
                else:
                    search_result = spotify.search(
                        query, type="track", limit=1)
                    if search_result:
                        related_tracks = search_result.get(
                            "tracks").get("items")
                        if len(related_tracks) > 0:
                            found_track = related_tracks[0]
                            track = parse_spotify_track_data(found_track)
                            cache.setex(
                                name=query,
                                time=SONG_CACHE_EXPIRY,
                                value=track.model_dump_json(),
                            )
                if track is not None:
                    tracks.append(track)
                    total_duration += track.duration
                    track_count += 1
            similarity = 0

            return Playlist(
                id="",
                title="",
                description="",
                thumbnail="",
                author="",
                duration=total_duration,
                track_count=track_count,
                tracks=tracks,
                platform=platform,
                similarity=similarity,
            )
        case PlaylistSource.YOUTUBE:
            for query in data.search_queries:
                track: Optional[Track] = None

                cached_song = cache.get(query)
                if cached_song is not None:
                    track_json = json.loads(cached_song)  # type: ignore
                    track = Track(**track_json)
                else:
                    search_result = ytmusic.search(
                        query, "songs", limit=1)
                    if search_result:
                        track = parse_youtube_track_data(search_result[0])
                        cache.setex(
                            name=query,
                            time=SONG_CACHE_EXPIRY,
                            value=track.model_dump_json(),
                        )
                if track is not None:
                    tracks.append(track)
                    total_duration += track.duration
                    track_count += 1
            similarity = 0

            return Playlist(
                id="",
                title="",
                description="",
                thumbnail="",
                author="",
                duration=total_duration,
                track_count=track_count,
                tracks=tracks,
                platform=platform,
                similarity=similarity,
            )
