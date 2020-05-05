from flask import render_template
from flask_classful import FlaskView

from classify.sentiment import Sentiment


class HomeView(FlaskView):
    route_base = '/'

    def index(self):
        return render_template('homepage.html')


class MoodPlayerView(FlaskView):
    route_base = '/player'

    def index(self):
        button_sentiments = {}
        for sentiment in Sentiment:
            button_sentiments[{
                Sentiment.DENIAL: 'btn-danger',
                Sentiment.ANGER: 'btn-warning',
                Sentiment.BARGAINING: 'btn-info',
                Sentiment.DEPRESSION: 'btn-primary',
                Sentiment.ACCEPTANCE: 'btn-success',
            }[sentiment]] = sentiment.name
        return render_template('mood_player.html', button_sentiments=button_sentiments)
