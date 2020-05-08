import unittest

from classify.sentiment import Sentiment
from fixures.spotify import SpotifyTestConnector
from spotify.playlist import PlaylistManager


class PlaylistManagerTest(unittest.TestCase):
    def test_add_track_to_sentiment_playlist(self):
        playlist_manager = PlaylistManager(SpotifyTestConnector())
        playlist_manager.add_tracks_to_playlist(('2p9RbgJwcuxasdMrQBdDDA3p',), Sentiment.BARGAINING)
        self.assertEqual('2p9RbgJwcuxasdMrQBdDDA3p',
                         playlist_manager.tracks_in_playlist(Sentiment.BARGAINING)[0]['track']['id'])
