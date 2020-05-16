import unittest

from tests.web_testing_base import TestClientMixin


class TestHomeWeb(unittest.TestCase, TestClientMixin):

    def setUp(self):
        self._setup_testclient()

    def test_homepage(self):
        response = self.test_client.get('/', follow_redirects=False)
        self.assertEqual(200, response.status_code)
        self.assertIn(b'<h1>Sentiment player for your favorite music</h1>', response.data)
