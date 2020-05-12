import os
from unittest import TestCase

from sentiment.web import create_app


class TestAppConfigs(TestCase):

    def test_development(self):
        os.environ['FLASK_CONFIGURATION'] = 'development'
        app = create_app()
        self.assertTrue(app.config.get('DEBUG'))
        self.assertTrue(app.config.get('TESTING'))

    def test_testing(self):
        os.environ['FLASK_CONFIGURATION'] = 'testing'
        app = create_app()
        self.assertFalse(app.config.get('DEBUG'))
        self.assertTrue(app.config.get('TESTING'))

    def test_production(self):
        os.environ['FLASK_CONFIGURATION'] = 'production'
        app = create_app()
        self.assertFalse(app.config.get('DEBUG'))
        self.assertFalse(app.config.get('TESTING'))
