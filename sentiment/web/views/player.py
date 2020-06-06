from typing import List

from flask import render_template
from flask_classful import FlaskView

from sentiment.classify.sentiment import Sentiment
from sentiment.web.auth import SpotifyServiceMixin
from sentiment.web.base import DebugLogMixin


class CategoryPlayer(object):
    def __init__(self):
        pass


class MoodPlayerView(FlaskView, SpotifyServiceMixin, DebugLogMixin):
    route_base = '/player'

    def __init__(self):
        super().__init__()

    def index(self):
        return self.post()

    def post(self):
        self._log.debug('library is {}'.format(self._is_analysed() and 'analysed' or 'not analysed'))
        category_players: List[CategoryPlayer] = self.category_players()
        return render_template('player.html', is_loggedin=self._valid_login(), is_analysed=(self._is_analysed()),
                               username=self._username_if_logged_in(), auth_token=self.auth_service.auth_token,
                               category_players=category_players)

    def category_players(self):
        if not self._is_analysed():
            return
        category_players = []
        for sentiment in Sentiment:
            category_player = CategoryPlayer()
            category_player.name = sentiment
            playlist = self.auth_service.service_instance.playlist_manager.playlist_for_sentiment(sentiment)
            category_player.playlist_id = playlist['id']
            category_player.cover_url = 'images' in playlist and playlist['images'][0]['url']
            category_players.append(category_player)
        return category_players

    def _username_if_logged_in(self):
        return self._valid_login() and self.auth_service.service_instance.username()

    def _is_analysed(self):
        return self._valid_login() and self.auth_service.service_instance.is_analysed()
