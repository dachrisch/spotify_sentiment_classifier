from unittest import TestCase
from unittest.mock import patch

from sentiment.spotify.connector import SpotipyConnectionWrapper


class TestSpotifyConnectorCache(TestCase):

    def test_invoked_only_once(self):
        with patch('spotipy.Spotify') as spotimock:
            connection = SpotipyConnectionWrapper.from_token(None)

            connection.current_user()
            connection.current_user()

            connection.current_user_saved_tracks()
            connection.current_user_saved_tracks()

            connection.audio_features()
            connection.audio_features()

            connection.user_playlist_create(None, None)
            connection.user_playlist_create(None, None)

            connection.user_playlist_add_tracks(None, None, None)
            connection.user_playlist_add_tracks(None, None, None)

            connection.playlist_tracks(None, None)
            connection.playlist_tracks(None, None)

            connection.current_user_playlists()
            connection.current_user_playlists()

            spotimock.return_value.current_user.assert_called_once()
            spotimock.return_value.current_user_saved_tracks.assert_called_once()
            spotimock.return_value.current_user_playlists.assert_called_once()
            spotimock.return_value.user_playlist_create.assert_called_once()
            spotimock.return_value.user_playlist_add_tracks.assert_called_once()
            spotimock.return_value.audio_features.assert_called_once()
            spotimock.return_value.playlist_tracks.assert_called_once()
