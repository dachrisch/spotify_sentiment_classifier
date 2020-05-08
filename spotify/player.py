import logging

import spotipy

from classify.sentiment import Sentiment
from spotify.playlist import PlaylistManager


class Player(object):
    log = logging.getLogger(__name__)

    def __init__(self, spotify_connector: spotipy.Spotify):
        self.spotify_connector = spotify_connector

    def queue_sentiment_playlist(self, sentiment: Sentiment):
        playlist_manager = PlaylistManager(self.spotify_connector)
        playlist_uri = playlist_manager.get_playlist_uri(sentiment)

        device_id = self.spotify_connector.devices()['devices'][0]['id']
        self.spotify_connector.add_to_queue(playlist_uri, device_id)
