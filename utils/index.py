import random
import string
from difflib import SequenceMatcher
from typing import List
from operator import attrgetter

from models.index import Track


class PlaylistSource:
    source: str
    playlist_id: str

    def __init__(self, source: str, playlist_id: str) -> None:
        self.source = source
        self.playlist_id = playlist_id


def get_playlist_source(url: str) -> PlaylistSource:
    if url.startswith('https://music.youtube.com'):
        return PlaylistSource('YOUTUBE', url.split("=")[-1].strip())
    elif url.startswith('https://open.spotify.com'):
        return PlaylistSource('SPOTIFY', url.split('/')[-1].strip())
    else:
        return None


def get_playlist_duration(duration: int) -> str:
    """
    Convert milliseconds to format (e.g 2 hours, 30 minutes)
    """
    hours = int(duration / 3600000)
    minutes = int((duration - (3600000 * hours)) / 60000)

    def is_plural(time: int) -> str:
        if time > 1:
            return "s"
        else:
            return ""
    if hours > 0:
        return f"{hours} hour{is_plural(hours)}, {minutes} minute{is_plural(minutes)}"
    else:
        return f"{minutes} minute{is_plural(minutes)}"


def get_track_duration(duration: int) -> str:
    """
    Convert milliseconds to format (e.g 2:32)
    """
    minutes = int(duration / 60000)
    seconds = int((duration - (60000 * minutes)) / 1000)

    def to_tens(num: int):
        if (num < 9):
            return f"{str(num)}0"
        else:
            return str(num)
    return f"{minutes}:{to_tens(seconds)}"


def track_duration_ms(duration: str) -> int:
    """
    Convert format 2:32 to milliseconds
    """
    minutes = int(duration.split(":")[0])
    seconds = int(duration.split(":")[1])
    return (minutes * 60000) + (seconds * 1000)


def get_spotify_track_data(track: dict) -> dict:
    artists = ""
    for artist in track.get("artists"):
        if track.get("artists")[-1].get("name") != artist.get("name"):
            artists += (artist.get("name") + ", ")
        else:
            artists += artist.get("name")
    return {
        "id": track.get("href").split("/")[-1],
        "title": track.get("name"),
        "url": "https://open.spotify.com/track/" + track.get("href").split("/")[-1],
        "artists": artists,
        "duration": get_track_duration(track.get("duration_ms")),
        "thumbnail": track.get("album").get("images")[0].get("url"),
        "album": track.get("album").get("name"),
        "isExplicit": track.get("explicit"),
        "searchKey": track.get("name"),
        "platform": "SPOTIFY",

    }


def get_youtube_track_data(track: dict) -> dict:
    artists = ""
    for artist in track.get("artists"):
        if track.get("artists")[-1].get("name") != artist.get("name"):
            artists += (artist.get("name") + ", ")
        else:
            artists += artist.get("name")
    return {
        "id": track.get("videoId"),
        "title": track.get("title"),
        "url": "https://music.youtube.com/watch?v=" + track.get("videoId"),
        "artists": artists,
        "duration": track.get("duration"),
        "thumbnail": track.get("thumbnails")[0].get("url"),
        "album": track.get("album").get("name") if track.get("album") is not None else "",
        "isExplicit": track.get("isExplicit"),
        "searchKey": track.get("title"),
        "platform": "YOUTUBE",
    }


def generate_random_string(length: int) -> str:
    return ''.join((random.choice(string.ascii_lowercase)
                    for x in range(length)))
