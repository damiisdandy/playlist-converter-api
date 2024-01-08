import os
import redis
from typing import List
from app.constants import SONG_CACHE_EXPIRY
from app.utils.parse_track import parse_spotify_track_data, parse_youtube_track_data

from app.utils.parser import get_playlist_source
from app.services.spotify import spotify, SpotifyException
from app.services.youtube import ytmusic
from app.models.main import Playlist, PlaylistSource, Track


class PlaylistNotFound(Exception):
    """Exception raised when playlist does not exist on platform

    """

    def __init__(self, platform: PlaylistSource) -> None:
        self.platform = platform
        self.message = f"Playlist not found on {platform}"
        super().__init__(self.message)


class InvalidPlaylistUrl(Exception):
    """Exception raised when playlist url is invalid

    """

    def __init__(self) -> None:
        self.message = "Playlist url is invalid"
        super().__init__(self.message)


def create_redis() -> redis.Redis:
    """connect to redis

    Returns:
        _type_: Redis
    """
    pool = redis.ConnectionPool.from_url(os.getenv("REDIS_URL"))
    return redis.Redis(connection_pool=pool)


def fetch_playlist_from_url(url: str) -> Playlist:
    """fetch playlist from url

    Args:
        url (str): either spotify or youtube playlist url

    Raises:
        PlaylistNotFound: playlist does not exist on platform
        InvalidPlaylistUrl: playlist url is invalid

    Returns:
        Playlist: Playlist object
    """
    cache = create_redis()

    playlist_info = get_playlist_source(url)
    if playlist_info is None:
        raise InvalidPlaylistUrl()

    match playlist_info.source:
        case PlaylistSource.SPOTIFY:
            try:
                spotify_playlist = spotify.playlist(
                    playlist_id=playlist_info.playlist_id
                )
            except SpotifyException:
                raise PlaylistNotFound(PlaylistSource.SPOTIFY)
            if spotify_playlist is None:
                raise PlaylistNotFound(PlaylistSource.SPOTIFY)
            tracks = spotify_playlist.get("tracks").get("items")
            parsed_tracks: List[Track] = []
            duration = 0

            for track in tracks:
                song = track.get("track")
                if song is not None:
                    parsed_song = parse_spotify_track_data(song)
                    duration += parsed_song.duration
                    parsed_tracks.append(parsed_song)

                    cache.setex(
                        name=parsed_song.spotify_search_query,
                        time=SONG_CACHE_EXPIRY,
                        value=parsed_song.model_dump_json(),
                    )

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
                raise PlaylistNotFound(PlaylistSource.YOUTUBE)
            if youtube_playlist is None:
                raise PlaylistNotFound(PlaylistSource.YOUTUBE)

            tracks = youtube_playlist.get("tracks")
            parsed_tracks: List[Track] = []

            if tracks:
                for track in tracks:
                    parsed_song = parse_youtube_track_data(track)
                    parsed_tracks.append(parsed_song)

                    cache.setex(
                        name=parsed_song.youtube_search_query,
                        time=SONG_CACHE_EXPIRY,
                        value=parsed_song.model_dump_json(),
                    )

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
