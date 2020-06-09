from flask import render_template
from flask_classful import FlaskView


class SliderView(FlaskView):
    route = '/slider'

    def index(self):
        return render_template('hello_slider.html')
