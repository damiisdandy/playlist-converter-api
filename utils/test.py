import unittest
from utils.url_parser import get_playlist_source
from utils.parse_track_object import parse_spotify_track_data
from models.index import PlaylistSource


class TestUtilities(unittest.TestCase):
    def test_spotify_url(self):
        url = "https://open.spotify.com/playlist/playlist_id?si=random_query"
        playlist_info = get_playlist_source(url)
        self.assertIsNotNone(playlist_info)
        if playlist_info is not None:
            self.assertEqual(playlist_info.source, PlaylistSource.SPOTIFY)
            self.assertEqual(playlist_info.playlist_id,
                             "playlist_id")

    def test_invalid_url(self):
        url = "https://google.com/playlist/playlist_id"
        playlist_info = get_playlist_source(url)
        self.assertIsNone(playlist_info)

class TestObjectParser(unittest.TestCase):
    def test_spotify_track_parser(self):
        