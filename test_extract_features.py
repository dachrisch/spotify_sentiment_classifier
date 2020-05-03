import unittest

from classify.classify import FeatureClassifier, SpotifyMoodClassification
from classify.sentiment import Sentiment
from fixures.spotify import SpotifyTestConnector
from spotify.playlist import PlaylistManager


class ExtractFeaturesTest(unittest.TestCase):

    def test_classify(self):
        self.assertEqual(Sentiment.BARGAINING, FeatureClassifier(SpotifyTestConnector()).classify({'valence': 0.56}))


class PlaylistManagerTest(unittest.TestCase):
    def test_create_playlists_when_empty(self):
        playlist_manager = PlaylistManager(SpotifyTestConnector())
        playlist_manager.create_playlists()
        self.assertEqual(set(playlist_manager._to_playlist(sentiment) for sentiment in Sentiment),
                         set(playlist_manager.available_playlists()))

    def test_create_playlists_when_not_empty(self):
        test_connector = SpotifyTestConnector()
        test_connector.playlists['items'].append({'name': 'gm_mood_1'})
        playlist_manager = PlaylistManager(test_connector)
        playlist_manager.create_playlists()
        self.assertEqual(set(playlist_manager._to_playlist(sentiment) for sentiment in Sentiment),
                         set(playlist_manager.available_playlists()))

    def test_add_song_to_sentiment_playlist(self):
        playlist_manager = PlaylistManager(SpotifyTestConnector())
        playlist_manager.add_songs_to_playlist(('2p9RbgJwcuxasdMrQBdDDA3p',), Sentiment.BARGAINING)
        self.assertIn({'track': {'id': '2p9RbgJwcuxasdMrQBdDDA3p', 'name': 'bargaining'}},
                      playlist_manager.songs_in_playlist(Sentiment.BARGAINING))


class SpotifyMoodClassificationTest(unittest.TestCase):
    def test_classify_and_add(self):
        test_connector = SpotifyTestConnector()
        SpotifyMoodClassification(test_connector, FeatureClassifier(test_connector)).perform()

        self.assertIn({'track': {'id': '2p9RbgJwcuxMrQBhdDDA3p', 'name': 'bargaining'}},
                      PlaylistManager(test_connector).songs_in_playlist(Sentiment.BARGAINING))
        self.assertIn({'track': {'id': '6lXKNdOsnaLv9LwulZbxNl', 'name': 'depression'}},
                      PlaylistManager(test_connector).songs_in_playlist(Sentiment.DEPRESSION))
        self.assertIn({'track': {'id': '3MVbvj0L7RTJy2CZYtf2c7', 'name': 'denial'}},
                      PlaylistManager(test_connector).songs_in_playlist(Sentiment.DENIAL))
        self.assertIn({'track': {'id': '5AIYDx0HUjra5Bn0vZtjmd', 'name': 'acceptance'}},
                      PlaylistManager(test_connector).songs_in_playlist(Sentiment.ACCEPTANCE))
        self.assertIn({'track': {'id': '2rnuW7ZTLSWT54yYvVaKT1', 'name': 'anger'}},
                      PlaylistManager(test_connector).songs_in_playlist(Sentiment.ANGER))


if __name__ == '__main__':
    unittest.main()
