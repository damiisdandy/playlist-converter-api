from typing import Optional
from app.models.main import PlaylistInitInfo, PlaylistSource
from urllib.parse import urlparse


def get_playlist_source(url: str) -> Optional[PlaylistInitInfo]:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    if domain == 'music.youtube.com':
        playlist_id = url.split("=")[-1].strip()
        return PlaylistInitInfo(PlaylistSource.YOUTUBE, playlist_id=playlist_id)
    elif domain == 'open.spotify.com':
        playlist_id = parsed_url.path.split('/')[-1].strip()
        return PlaylistInitInfo(PlaylistSource.SPOTIFY, playlist_id=playlist_id)
    else:
        return None
