from pydantic import BaseModel
from typing import List, Optional


class Track(BaseModel):
    id: str
    title: str
    url: str
    artists: str
    duration: str
    thumbnail: str
    album: str
    isExplicit: bool
    searchKey: str
    platform: Optional[str]


class Playlist(BaseModel):
    id: str
    title: str
    description: str
    thumbnail: str
    author: str
    year: str
    duration: str
    trackCount: int
    tracks: List[Track]
    platform: str
    similarity: Optional[float] = 0.0


class GetPlaylist(BaseModel):
    url: str


class GeneratePlaylist(BaseModel):
    thumbnail: str
    platform: str
    tracks: List[Track]
