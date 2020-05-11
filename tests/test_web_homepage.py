import unittest

from bs4 import BeautifulSoup

from tests.web_testing_base import WithTestClientMixin


class TestHomeWeb(unittest.TestCase, WithTestClientMixin):

    def setUp(self):
        self._setup_testclient()

    def test_homepage(self):
        response = self.test_client.get('/', follow_redirects=False)
        self.assertEqual(200, response.status_code)
        self.assertIn(b'<h1>Sentiment player for your favorite music</h1>', response.data)

    def test_message_is_displayed(self):
        response = self.test_client.get('/?error="Test"', follow_redirects=False)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.data, features='html.parser')
        error_messages = soup.find(id='error_messages')

        self.assertIsNotNone(error_messages)
