import unittest

from classify.sentiment import Sentiment
from fixures.spotify import SpotipyTestFixure
from spotify.playlist import PlaylistManager
from spotify.service import SpotifyMoodClassificationService


class SpotifyMoodClassificationServiceTest(unittest.TestCase):
    def test_classify_and_add(self):
        test_connector = SpotipyTestFixure.as_wrapper()
        SpotifyMoodClassificationService(test_connector).analyse()

        self.assertEqual('2p9RbgJwcuxMrQBhdDDA3p',
                         PlaylistManager(test_connector).tracks_in_playlist(Sentiment.BARGAINING)[0]['track']['id'])
        self.assertEqual('6lXKNdOsnaLv9LwulZbxNl',
                         PlaylistManager(test_connector).tracks_in_playlist(Sentiment.DEPRESSION)[0]['track']['id'])
        self.assertEqual('3MVbvj0L7RTJy2CZYtf2c7',
                         PlaylistManager(test_connector).tracks_in_playlist(Sentiment.DENIAL)[0]['track']['id'])
        self.assertEqual('5AIYDx0HUjra5Bn0vZtjmd',
                         PlaylistManager(test_connector).tracks_in_playlist(Sentiment.ACCEPTANCE)[0]['track']['id'])
        self.assertEqual('2rnuW7ZTLSWT54yYvVaKT1',
                         PlaylistManager(test_connector).tracks_in_playlist(Sentiment.ANGER)[0]['track']['id'])

    def test_is_not_analysed(self):
        self.assertFalse(SpotifyMoodClassificationService(SpotipyTestFixure.as_wrapper()).is_analysed())

    def test_is_analysed(self):
        test_connector = SpotipyTestFixure.as_wrapper()
        playlist_manager = PlaylistManager(test_connector)
        for sentiment in Sentiment:
            playlist_manager.add_tracks_to_playlist(('2p9RbgJwcuxasdMrQBdDDA3p',), sentiment)
        self.assertTrue(SpotifyMoodClassificationService(test_connector).is_analysed())
