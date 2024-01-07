

def parse_spotify_track_data(track: dict) -> dict
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
