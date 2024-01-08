from typing import Optional
from app.models.main import PlaylistInitInfo, PlaylistSource
from urllib.parse import urlparse, parse_qs
import re


def get_playlist_source(url: str) -> Optional[PlaylistInitInfo]:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    if domain == 'music.youtube.com':
        playlist_id = parse_qs(parsed_url.query).get('list')
        if playlist_id is None:
            return None
        return PlaylistInitInfo(PlaylistSource.YOUTUBE, playlist_id=playlist_id[0])
    elif domain == 'open.spotify.com':
        playlist_id = parsed_url.path.split('/')[-1].strip()
        return PlaylistInitInfo(PlaylistSource.SPOTIFY, playlist_id=playlist_id)
    else:
        return None


def remove_feat_suffix(text):
    # Remove characters after "feat"
    text = re.sub(r'\sfeat\..*$', '', text, flags=re.IGNORECASE)
    # Remove characters after "(feat"
    text = re.sub(r'\(feat\..*$', '', text, flags=re.IGNORECASE)

    return text.strip()
