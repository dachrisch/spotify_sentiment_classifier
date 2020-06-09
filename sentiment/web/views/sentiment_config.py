from flask import url_for, render_template
from flask_classful import FlaskView, route
from flask_table import Table, Col
from werkzeug.utils import redirect

from sentiment.classify.classify import RuleHandlerBuilder
from sentiment.classify.sentiment import Sentiment
from sentiment.web.auth import SpotifyServiceMixin
from sentiment.web.base import DebugLogMixin


class SongsTable(Table):
    name = Col('name')
    artist = Col('artist')
    album = Col('album')


class ConfigView(FlaskView, SpotifyServiceMixin, DebugLogMixin):
    route_base = '/config'

    def index(self):
        if not self._valid_login():
            self._log.debug('redirecting for authentication...')
            return redirect(url_for('LoginView:index', next=url_for('ConfigView:index')))

        tracks = self.auth_service.service_instance.spotify_connector.current_user_saved_tracks()['items']
        songs_table = self._to_table(tracks)

        sentiment_tables = {}
        for sentiment in Sentiment:
            playlist = self.auth_service.service_instance.playlist_manager.playlist_for_sentiment(sentiment)
            tracks = self.auth_service.service_instance.spotify_connector.playlist_tracks(playlist['id'],
                                                                                          fields='items(track(name, album(name), artists(name)))')[
                'items']
            sentiment_tables[sentiment.name] = self._to_table(tracks)
        return render_template('config.html', table=songs_table, sentiment_tables=sentiment_tables,
                               auth_token=self.auth_service.auth_token, )

    @route('sentiment')
    def sentiment(self):
        return render_template('sentiment_config.html', handlers=list(RuleHandlerBuilder.default()))

    def _to_table(self, tracks):
        songs_table = SongsTable([])
        for track in tracks:
            track_name = track['track']['name']
            if 'album' in track['track']:
                album_name = track['track']['album']['name']
            else:
                album_name = 'None'

            if 'artists' in track['track']:
                artist_names = '&'.join(map(lambda x: x['name'], track['track']['artists']))
            else:
                artist_names = 'None'
            songs_table.items.append({'name': track_name, 'album': album_name, 'artist': artist_names})
        return songs_table
