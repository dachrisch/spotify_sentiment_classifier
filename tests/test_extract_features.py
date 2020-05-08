import json
import unittest
from importlib import resources
from logging import config

from classify.classify import FeatureClassifier, SpotifyMoodClassification
from classify.sentiment import Sentiment
from fixures.spotify import SpotifyTestConnector
from spotify.playlist import PlaylistManager

with resources.open_text('tests', 'tests_logging.json') as f:
    config.dictConfig(json.load(f)['logging'])


class ExtractFeaturesTest(unittest.TestCase):

    def test_classify(self):
        self.assertEqual(Sentiment.BARGAINING, FeatureClassifier().classify({'valence': 0.56}))


class PlaylistManagerTest(unittest.TestCase):
    def test_add_track_to_sentiment_playlist(self):
        playlist_manager = PlaylistManager(SpotifyTestConnector())
        playlist_manager.add_tracks_to_playlist(('2p9RbgJwcuxasdMrQBdDDA3p',), Sentiment.BARGAINING)
        self.assertEqual('2p9RbgJwcuxasdMrQBdDDA3p',
                         playlist_manager.tracks_in_playlist(Sentiment.BARGAINING)[0]['track']['id'])


class SpotifyMoodClassificationTest(unittest.TestCase):
    def test_classify_and_add(self):
        test_connector = SpotifyTestConnector()
        SpotifyMoodClassification(test_connector).analyse()

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
        self.assertFalse(SpotifyMoodClassification(SpotifyTestConnector()).is_analysed())

    def test_is_analysed(self):
        test_connector = SpotifyTestConnector()
        playlist_manager = PlaylistManager(test_connector)
        for sentiment in Sentiment:
            playlist_manager.add_tracks_to_playlist(('2p9RbgJwcuxasdMrQBdDDA3p',), sentiment)
        self.assertTrue(SpotifyMoodClassification(test_connector).is_analysed())


if __name__ == '__main__':
    unittest.main()
