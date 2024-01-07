from models.index import PlaylistSource, Track


def parse_spotify_track_data(track: dict) -> Track:
    artists = ""
    track_id = ""
    album_name = ""
    album_image = "https://placehold.co/640x640.png"
    artist_list = track.get("artists")

    if artist_list is not None:
        artist_names_list = [artist.get("name") for artist in artist_list]
        artists = ", ".join(artist_names_list)

    track_id = track.get("id") or ""
    album = track.get("album")
    if album is not None:
        album_name = album.get("name")
        album_image = album.get("images")[0].get("url")

    return Track(
        id=track_id,
        title=track.get("name") or "",
        url=f"https://open.spotify.com/track/{track_id}",
        artists=artists,
        duration=track.get("duration_ms") or 0,
        thumbnail=album_image,
        album=album_name,
        is_explicit=track.get("explicit") or False,
        search_key=track.get("name") or "",
        platform=PlaylistSource.SPOTIFY,
    )
