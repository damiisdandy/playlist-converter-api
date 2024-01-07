import unittest
from utils.index import get_playlist_source
from models.index import PlaylistSource


class TestURLParsing(unittest.TestCase):
    def test_spotify_url(self):
        url = 'https://open.spotify.com/playlist/playlist_id?si=random_query'
        playlist_info = get_playlist_source(url)
        self.assertEqual(playlist_info.source, PlaylistSource.SPOTIFY)
        self.assertEqual(playlist_info.playlist_id, 'playlist_id')


if __name__ == '__main__':
    unittest.main()
