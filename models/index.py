from pydantic import BaseModel
from typing import List, Optional
import enum


class PlaylistSource(enum.Enum):
    YOUTUBE = 'YOUTUBE'
    SPOTIFY = 'SPOTIFY'


class PlaylistInitInfo:
    source: PlaylistSource
    playlist_id: str

    def __init__(self, source: PlaylistSource, playlist_id: str) -> None:
        self.source = source
        self.playlist_id = playlist_id


class Track(BaseModel):
    id: str
    title: str
    url: str
    artists: str
    duration: int
    thumbnail: str
    album: str
    is_explicit: bool
    search_key: str
    platform: PlaylistSource


class Playlist(BaseModel):
    id: str | int
    title: str
    description: str
    thumbnail: str
    author: str
    duration: int
    track_count: int
    tracks: List[Track]
    platform: PlaylistSource
    similarity: Optional[float]


class GetPlaylist(BaseModel):
    url: str


class GeneratePlaylist(BaseModel):
    thumbnail: str
    platform: str
    tracks: List[Track]
