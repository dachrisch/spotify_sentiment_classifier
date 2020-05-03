import logging

import spotipy

from classify.sentiment import Sentiment


class PlaylistManager(object):
    def __init__(self, spotify_connector: spotipy.Spotify):
        self.spotify_connector = spotify_connector
        self.log = logging.getLogger(__name__)

    def available_playlists(self):
        return tuple(map(lambda x: x['name'], self.spotify_connector.current_user_playlists()['items']))

    def create_playlists(self):
        mood_lists = (self._to_playlist(sentiment) for sentiment in Sentiment)
        for list_name in filter(lambda x: x not in self.available_playlists(), mood_lists):
            self.log.debug('creating playlist [%s]' % list_name)
            self.spotify_connector.user_playlist_create(self.spotify_connector.current_user()['id'], list_name, False)

    def songs_in_playlist(self, sentiment: Sentiment):
        return self.spotify_connector.playlist_tracks(self._to_playlist(sentiment), fields='items(track(name,id))')[
            'items']

    def add_songs_to_playlist(self, song_ids, sentiment: Sentiment):
        self.log.debug('adding [%d] songs to playlist [%s]' % (len(song_ids), sentiment))
        self.spotify_connector.user_playlist_add_tracks(self.spotify_connector.current_user()['id'],
                                                        self._to_playlist(sentiment), song_ids)

    @staticmethod
    def _to_playlist(sentiment: Sentiment):
        return {
            Sentiment.DENIAL: 'gm_mood_1',
            Sentiment.ANGER: 'gm_mood_2',
            Sentiment.BARGAINING: 'gm_mood_3',
            Sentiment.DEPRESSION: 'gm_mood_4',
            Sentiment.ACCEPTANCE: 'gm_mood_5',
        }[sentiment]
