from app.models.main import PlaylistSource, Track

DEFAULT_THUMBNAIL = "https://placehold.co/640x640.png"


def parse_spotify_track_data(track: dict) -> Track:
    """Parse JSON respons from Spotify API into Track object

    Args:
        track (dict): JSON response from Spotify API

    Returns:
        Track: Track object
    """
    artists = ""
    track_id = ""
    album_name = ""
    album_image = DEFAULT_THUMBNAIL
    artist_list = track.get("artists")
    first_artist = ""

    if artist_list is not None:
        artist_names_list = [artist.get("name") for artist in artist_list]
        first_artist = artist_names_list[0]
        artists = ", ".join(artist_names_list)

    track_id = track.get("id") or ""
    album = track.get("album")
    if album is not None:
        album_name = album.get("name")
        album_image = album.get("images")[0].get("url")

    title = track.get("name") or ""

    youtube_search_query = f'"{title}" by {first_artist}'
    spotify_search_query = f"{title} artist:{first_artist} album:{album_name}"

    return Track(
        id=track_id,
        title=title,
        url=f"https://open.spotify.com/track/{track_id}",
        artists=artists,
        duration=track.get("duration_ms") or 0,
        thumbnail=album_image,
        album=album_name,
        is_explicit=track.get("explicit") or False,
        platform=PlaylistSource.SPOTIFY,
        spotify_search_query=spotify_search_query,
        youtube_search_query=youtube_search_query,
    )


def parse_youtube_track_data(track: dict) -> Track:
    """Parse JSON respons from Youtube API into Track object

    Args:
        track (dict): JSON response from Youtube API

    Returns:
        Track: Track object
    """
    artists = ""
    thumbnail = DEFAULT_THUMBNAIL
    artists_list = track.get("artists")
    first_artist = artists_list[0].get(
        "name") if artists_list is not None else ""
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

    title = track.get("title") or ""

    spotify_search_query = f"{title} artist:{first_artist} album:{album_name}"
    youtube_search_query = f'"{title}" by {first_artist}'

    return Track(
        id=track_id,
        title=title,
        url=f"https://music.youtube.com/watch?v={track_id}",
        artists=artists,
        duration=(track.get("duration_seconds") or 0) * 1000,
        thumbnail=thumbnail,
        album=album_name,
        is_explicit=track.get("isExplicit") or False,
        platform=PlaylistSource.YOUTUBE,
        spotify_search_query=spotify_search_query,
        youtube_search_query=youtube_search_query,
    )
