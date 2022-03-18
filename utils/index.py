
class PlaylistSource:
    source: str
    playlist_id: str

    def __init__(self, source: str, playlist_id: str) -> None:
        self.source = source
        self.playlist_id = playlist_id


def get_playlist_source(url: str) -> PlaylistSource:
    if url.startswith('https://music.youtube.com'):
        return PlaylistSource('YOUTUBE', url.split("=")[-1])
    elif url.startswith('https://open.spotify.com'):
        return PlaylistSource('SPOTIFY', url.split('/')[-1])
    elif url.startswith('https://'):
        return PlaylistSource('APPLE', url.split('/')[-1])
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
