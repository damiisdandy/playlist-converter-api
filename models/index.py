from pydantic import BaseModel
from typing import List


class Track(BaseModel):
    title: str
    url: str
    artists: str
    duration: str
    thumbnail: str
    album: str
    isExplicit: bool
    searchKey: str


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


class GetPlaylist(BaseModel):
    url: str
