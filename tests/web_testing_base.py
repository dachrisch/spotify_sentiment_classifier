import os

from flask_dance.consumer.storage import MemoryStorage

from app import create_app
from sentiment.classify.sentiment import Sentiment
from sentiment.web.views import HomeView, AnalyseView, MoodPlayerView
from tests.fixtures.spotify import SpotifyAuthenticationTestService


class WithTestClientMixin(object):
    def _setup_testclient(self):
        HomeView.service = SpotifyAuthenticationTestService()
        AnalyseView.service = SpotifyAuthenticationTestService()
        MoodPlayerView.service = SpotifyAuthenticationTestService()
        os.environ['FLASK_CONFIGURATION'] = 'development'
        app = create_app()
        self.storage = MemoryStorage({'access_token': 'fake-token', 'expires_in': 1})
        app.blueprints['spotify'].storage = self.storage
        self.test_client = app.test_client()

    def _setup_account_as_analysed(self):
        for sentiment in Sentiment:
            HomeView.service.with_token(None).playlist_manager.add_tracks_to_playlist(('2p9RbgJwcuxasdMrQBdDDA3p',),
                                                                                      sentiment)
            MoodPlayerView.service.with_token(None).playlist_manager.add_tracks_to_playlist(
                ('2p9RbgJwcuxasdMrQBdDDA3p',),
                sentiment)


class WasAnalysedCatcher(object):
    def __init__(self):
        self._analyse_was_analysed = False

    # noinspection PyUnusedLocal
    def with_token(self, token):
        return self

    def analyse(self):
        self._analyse_was_analysed = True
        return True

    def analyse_was_called(self):
        return self._analyse_was_analysed
