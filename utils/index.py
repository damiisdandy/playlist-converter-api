
def get_playlist_source(url: str):
    if url.startswith('https://music.youtube.com'):
        return {
            "source": 'YOUTUBE',
            "playlist_id": url.split("=")[-1]
        }
    else:
        return None
