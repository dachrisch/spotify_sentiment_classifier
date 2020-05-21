import logging

from flask import render_template, request, url_for, flash, session, g
from flask_classful import FlaskView
from flask_dance.contrib.spotify import spotify
from flask_table import Table, Col
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import SubmitField

from sentiment.classify.sentiment import Sentiment
from sentiment.spotify.service import UserHasNoTracksException
from sentiment.web.auth import SpotifyServiceMixin, BeforeRequestDispatcherMixin


class DebugLogMixin(BeforeRequestDispatcherMixin):
    def __init__(self):
        super().__init__()
        self._log = logging.getLogger(__name__)
        self._before_request_funcs.append(self._debug_log)

    def _debug_log(self, name):
        self._log.debug('requesting [{}::{}]'.format(self.__class__.__name__, name))
        self._log.debug('Session: {}'.format(session))
        self._log.debug('App Context: {}'.format(g.__dict__))
        self._log.debug('Spotify: {}'.format(spotify.__dict__))


class HomeView(FlaskView, SpotifyServiceMixin, DebugLogMixin):
    route_base = '/'

    def __init__(self):
        super().__init__()

    def index(self):
        if session.get('next_url'):
            return redirect(session.pop('next_url'))
        return render_template('homepage.html')


class LoginView(FlaskView, DebugLogMixin):
    route_base = '/login'

    def index(self):
        session['next_url'] = request.args.get('next')
        return redirect(url_for('spotify.login'))


class AnalyseView(FlaskView, SpotifyServiceMixin, DebugLogMixin):
    route_base = '/analyse'

    def __init__(self):
        super().__init__()

    def post(self):
        if not self._valid_login():
            self._log.debug('redirecting for authentication...')
            return redirect(url_for('LoginView:index', next=url_for('AnalyseView:post')))
        try:
            self.auth_service.service_instance.analyse()
            return redirect(url_for('MoodPlayerView:index'))
        except UserHasNoTracksException as e:
            self._log.exception(e)
            flash("Analyse failed! You don't have any saved tracks.", 'error')
            return redirect(url_for('MoodPlayerView:index'))


class MoodPlayerView(FlaskView, SpotifyServiceMixin, DebugLogMixin):
    route_base = '/player'

    def __init__(self):
        super().__init__()

    def index(self):
        return self.post()

    def post(self):
        self._log.debug(
            'library is {}'.format(self._is_analysed() and 'analysed' or 'not analysed'))
        form = SentimentForm(request.form)
        return render_template('player.html', form=form, is_loggedin=self._valid_login(),
                               is_analysed=(self._is_analysed()), username=self._username_if_logged_in(),
                               playlist_id=(self._playlist_id_from_form(form)), auth_token=self.auth_service.auth_token)

    def _username_if_logged_in(self):
        return self._valid_login() and self.auth_service.service_instance.username()

    def _playlist_id_from_form(self, form: FlaskForm):
        sentiment_name = None
        if self._is_analysed() and form.is_submitted():
            for name, value in form.data.items():
                if value:
                    sentiment_name = name
                    break
        playlist_id = None
        if sentiment_name:
            sentiment = Sentiment.__getitem__(sentiment_name)
            playlist_id = self.auth_service.service_instance.playlist_manager.playlist_for_sentiment(sentiment)['id']
        return playlist_id

    def _is_analysed(self):
        return self._valid_login() and self.auth_service.service_instance.is_analysed()


class SliderView(FlaskView):
    route = '/slider'

    def index(self):
        return render_template('hello_slider.html')


class SongsTable(Table):
    name = Col('name')
    artist = Col('artist')
    album = Col('album')


class ConfigView(FlaskView, SpotifyServiceMixin, DebugLogMixin):
    route = '/config'

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
        return render_template('config.html', table=songs_table, sentiment_tables=sentiment_tables)

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


def with_sentiment_buttons(cls):
    for sentiment in Sentiment:
        setattr(cls, sentiment.name, SubmitField(sentiment.name))
    return cls


@with_sentiment_buttons
class SentimentForm(FlaskForm):

    def __init__(self, form=None):
        super(SentimentForm, self).__init__(form)

    def sentiment_buttons(self):
        for sentiment in Sentiment:
            yield getattr(self, sentiment.name)
