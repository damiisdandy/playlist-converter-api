import os
import json


from typing import List, Optional
from redis import Redis
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.dependencies import InvalidPlaylistUrl, PlaylistNotFound, create_redis, fetch_playlist_from_url
from app.constants import SONG_CACHE_EXPIRY
from app.utils.parser import get_playlist_source
from app.utils.parse_track import calculate_similarity, parse_spotify_track_data, parse_youtube_track_data
from app.models.main import GeneratePlaylist, GetPlaylist, Playlist, PlaylistSource, Track
from app.services.spotify import spotify
from app.services.youtube import ytmusic


# setup environment variables
load_dotenv()

# CORS
cors_origins_str = os.getenv("CORS_ORIGINS")
origins = cors_origins_str.split() if cors_origins_str else []

# FASTApi app
app = FastAPI()

# Middlewares
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
    try:
        playlist = fetch_playlist_from_url(data.url)

        return playlist
    except InvalidPlaylistUrl:
        raise HTTPException(status_code=400, detail="playlist url is invalid")
    except PlaylistNotFound:
        raise HTTPException(status_code=404, detail="playlist does not exist")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/generate-playlist", response_model=Playlist)
async def generate_playlist(data: GeneratePlaylist, cache: Redis = Depends(create_redis)) -> Playlist:
    url = data.playlist_url
    platform = data.convert_to

    playlist_source_from_url = get_playlist_source(url)
    if playlist_source_from_url is None or playlist_source_from_url.source == platform:
        raise HTTPException(
            status_code=400, detail="either playlist url is invalid or you are trying yo convert to the same platform")

    try:
        playlist = fetch_playlist_from_url(url)
    except InvalidPlaylistUrl:
        raise HTTPException(status_code=400, detail="playlist url is invalid")
    except PlaylistNotFound:
        raise HTTPException(status_code=404, detail="playlist does not exist")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

    tracks: List[Track] = []
    total_duration = 0
    track_count = 0
    total_similarity = 0

    match platform:
        case PlaylistSource.SPOTIFY:

            for gotten_track in playlist.tracks:
                track: Optional[Track] = None
                cached_song = cache.get(gotten_track.spotify_search_query)
                if cached_song is not None:
                    track_json = json.loads(cached_song)  # type: ignore
                    track = Track(**track_json)
                else:
                    search_result = spotify.search(
                        gotten_track.spotify_search_query, type="track", limit=1)
                    if search_result:
                        related_tracks = search_result.get(
                            "tracks").get("items")
                        if len(related_tracks) > 0:
                            found_track = related_tracks[0]
                            track = parse_spotify_track_data(found_track)
                            cache.setex(
                                name=gotten_track.spotify_search_query,
                                time=SONG_CACHE_EXPIRY,
                                value=track.model_dump_json(),
                            )
                if track is not None:
                    tracks.append(track)
                    total_similarity += calculate_similarity(
                        gotten_track, track)
                    total_duration += track.duration
                    track_count += 1

            similarity = total_similarity / track_count if track_count > 0 else 0

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
                similarity=(similarity / 4) * 100,
            )
        case PlaylistSource.YOUTUBE:
            for gotten_track in playlist.tracks:
                track: Optional[Track] = None

                cached_song = cache.get(gotten_track.youtube_search_query)
                if cached_song is not None:
                    track_json = json.loads(cached_song)  # type: ignore
                    track = Track(**track_json)
                else:
                    search_result = ytmusic.search(
                        gotten_track.youtube_search_query, "songs", limit=1)
                    if search_result:
                        track = parse_youtube_track_data(search_result[0])
                        cache.setex(
                            name=gotten_track.youtube_search_query,
                            time=SONG_CACHE_EXPIRY,
                            value=track.model_dump_json(),
                        )
                if track is not None:
                    tracks.append(track)
                    total_similarity += calculate_similarity(
                        gotten_track, track)
                    total_duration += track.duration
                    track_count += 1

            similarity = total_similarity / track_count if track_count > 0 else 0

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
                similarity=(similarity / 4) * 100,
            )
