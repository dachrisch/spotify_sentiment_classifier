import spotipy

from classify.sentiment import Sentiment


class PlaylistManager(object):
    def __init__(self, spotify_connector: spotipy.Spotify):
        self.spotify_connector = spotify_connector
        self.mood_lists = (self._to_playlist(sentiment) for sentiment in Sentiment)

    def available_playlists(self):
        return tuple(map(lambda x: x['name'], self.spotify_connector.current_user_playlists()['items']))

    def create_playlists(self):
        for list_name in filter(lambda x: x not in self.available_playlists(), self.mood_lists):
            self.spotify_connector.user_playlist_create(self.spotify_connector.current_user(), list_name, False)

    def songs_in_playlist(self, sentiment: Sentiment):
        return self.spotify_connector.playlist_tracks(sentiment, fields='items(track(name,id))')['items']

    def add_songs_to_playlist(self, song_ids, sentiment: Sentiment):
        self.spotify_connector.user_playlist_add_tracks(self.spotify_connector.current_user(), sentiment, song_ids)

    def _to_playlist(self, sentiment: Sentiment):
        return {
            Sentiment.DENIAL: 'gm_mood_1',
            Sentiment.ANGER: 'gm_mood_2',
            Sentiment.BARGAINING: 'gm_mood_3',
            Sentiment.DEPRESSION: 'gm_mood_4',
            Sentiment.ACCEPTANCE: 'gm_mood_5',
        }[sentiment]
