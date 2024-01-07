from models.index import PlaylistSource, Track

DEFAULT_THUMBNAIL = "https://placehold.co/640x640.png"


def parse_spotify_track_data(track: dict) -> Track:
    artists = ""
    track_id = ""
    album_name = ""
    album_image = DEFAULT_THUMBNAIL
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


def parse_youtube_track_data(track: dict) -> Track:
    artists = ""
    thumbnail = DEFAULT_THUMBNAIL
    artists_list = track.get("artists")
    if artists_list is not None:
        artist_names_list = [artist.get("name") for artist in artists_list]
        artists = ", ".join(artist_names_list)

    track_id = track.get("videoId") or ""
    thumbnails = track.get("thumbnails")
    if thumbnails is not None:
        thumbnail = thumbnails[0].get("url")
    album = track.get("album")
    album_name = ""
    if album is not None:
        album_name = album.get("name") or ""

    return Track(
        id=track_id,
        title=track.get("title") or "",
        url=f"https://music.youtube.com/watch?v={track_id}",
        artists=artists,
        duration=(track.get("duration_seconds") or 0) * 1000,
        thumbnail=thumbnail,
        album=album_name,
        is_explicit=track.get("isExplicit") or False,
        search_key=track.get("title") or "",
        platform=PlaylistSource.YOUTUBE,
    )
