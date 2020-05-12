import unittest

from sentiment.classify.sentiment import Sentiment
from sentiment.spotify.playlist import PlaylistManager
from tests.fixtures.spotify import SpotipyTestFixure


class PlaylistManagerTest(unittest.TestCase):
    def test_add_track_to_sentiment_playlist(self):
        playlist_manager = PlaylistManager(SpotipyTestFixure.as_wrapper())
        playlist_manager.add_tracks_to_playlist(('2p9RbgJwcuxasdMrQBdDDA3p',), Sentiment.BARGAINING)
        self.assertEqual('2p9RbgJwcuxasdMrQBdDDA3p',
                         playlist_manager.tracks_in_playlist(Sentiment.BARGAINING)[0]['track']['id'])

    def test_add_empty_track(self):
        fixture = SpotipyTestFixure()
        playlist_manager = PlaylistManager(SpotipyTestFixure.as_wrapper())
        playlist_manager.add_tracks_to_playlist((), Sentiment.BARGAINING)
        self.assertEqual((), playlist_manager.tracks_in_playlist(Sentiment.BARGAINING))
