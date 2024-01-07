import unittest
from utils.url_parser import get_playlist_source
from utils.parse_track import parse_spotify_track_data
from models.index import PlaylistSource

spotify_track_dict = {
    "album": {
        "album_type": "single",
        "artists": [
            {
                "external_urls": {
                    "spotify": "https://open.spotify.com/artist/6QSOpFwMSqDj21HVu34Wm1"
                },
                "href": "https://api.spotify.com/v1/artists/6QSOpFwMSqDj21HVu34Wm1",
                        "id": "6QSOpFwMSqDj21HVu34Wm1",
                        "name": "Xanemusic",
                        "type": "artist",
                        "uri": "spotify:artist:6QSOpFwMSqDj21HVu34Wm1",
            }
        ],
        "available_markets": [],
        "external_urls": {
            "spotify": "https://open.spotify.com/album/0H7JxfItYZm07zg0MXfN0o"
        },
        "href": "https://api.spotify.com/v1/albums/0H7JxfItYZm07zg0MXfN0o",
        "id": "0H7JxfItYZm07zg0MXfN0o",
        "images": [
            {
                "height": 640,
                "url": "https://i.scdn.co/image/ab67616d0000b2730ae89e52c656c3e05c362490",
                "width": 640,
            },
            {
                "height": 300,
                "url": "https://i.scdn.co/image/ab67616d00001e020ae89e52c656c3e05c362490",
                "width": 300,
            },
            {
                "height": 64,
                "url": "https://i.scdn.co/image/ab67616d000048510ae89e52c656c3e05c362490",
                "width": 64,
            },
        ],
        "name": "Motion (Remix)",
        "release_date": "2022-11-30",
        "release_date_precision": "day",
        "total_tracks": 3,
        "type": "album",
        "uri": "spotify:album:0H7JxfItYZm07zg0MXfN0o",
    },
    "artists": [
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/6QSOpFwMSqDj21HVu34Wm1"
            },
            "href": "https://api.spotify.com/v1/artists/6QSOpFwMSqDj21HVu34Wm1",
            "id": "6QSOpFwMSqDj21HVu34Wm1",
            "name": "Xanemusic",
            "type": "artist",
            "uri": "spotify:artist:6QSOpFwMSqDj21HVu34Wm1",
        }
    ],
    "available_markets": [],
    "disc_number": 1,
    "duration_ms": 156264,
    "episode": False,
    "explicit": False,
    "external_ids": {"isrc": "ARIXB2301668"},
    "external_urls": {
        "spotify": "https://open.spotify.com/track/59tmfKVyQBGTTehRuPbgct"
    },
    "href": "https://api.spotify.com/v1/tracks/59tmfKVyQBGTTehRuPbgct",
    "id": "59tmfKVyQBGTTehRuPbgct",
    "is_local": False,
    "name": "Who Is She x Supervillain (TikTok Edit) - Remix",
    "popularity": 0,
    "preview_url": None,
    "track": True,
    "track_number": 2,
    "type": "track",
    "uri": "spotify:track:59tmfKVyQBGTTehRuPbgct",
}


class TestUtilities(unittest.TestCase):
    def test_spotify_url(self):
        url = "https://open.spotify.com/playlist/playlist_id?si=random_query"
        playlist_info = get_playlist_source(url)
        self.assertIsNotNone(playlist_info)
        if playlist_info is not None:
            self.assertEqual(playlist_info.source, PlaylistSource.SPOTIFY)
            self.assertEqual(playlist_info.playlist_id, "playlist_id")

    def test_invalid_url(self):
        url = "https://google.com/playlist/playlist_id"
        playlist_info = get_playlist_source(url)
        self.assertIsNone(playlist_info)


class TestObjectParser(unittest.TestCase):
    def test_spotify_track_parser(self):
        spotify_track = parse_spotify_track_data(spotify_track_dict)
        self.assertEqual(spotify_track.id, "59tmfKVyQBGTTehRuPbgct")
        self.assertEqual(
            spotify_track.title, "Who Is She x Supervillain (TikTok Edit) - Remix"
        )
        self.assertEqual(
            spotify_track.url, "https://open.spotify.com/track/59tmfKVyQBGTTehRuPbgct"
        )
        self.assertEqual(spotify_track.artists, "Xanemusic")
        self.assertEqual(spotify_track.duration, 156264)

        self.assertEqual(spotify_track.thumbnail,
                         "https://i.scdn.co/image/ab67616d0000b2730ae89e52c656c3e05c362490")
        self.assertEqual(spotify_track.album, "Motion (Remix)")
        self.assertEqual(spotify_track.is_explicit, False)
        self.assertEqual(spotify_track.search_key,
                         "Who Is She x Supervillain (TikTok Edit) - Remix")
        self.assertEqual(spotify_track.platform, PlaylistSource.SPOTIFY)
