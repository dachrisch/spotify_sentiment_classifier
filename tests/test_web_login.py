import unittest

from tests.web_testing_base import WithTestClientMixin


class TestLoginWeb(unittest.TestCase, WithTestClientMixin):

    def setUp(self):
        self._setup_testclient()
        self._setup_logged_in()

    def test_token_expired_on_analyse(self):
        self._setup_token_expired()

        response = self.test_client.post('/analyse/', follow_redirects=False)
        self.assertEqual(302, response.status_code)
        self.assertIn(b'<a href="/login/?next=%2Fanalyse%2F">', response.data)

    def test_login_flow_with_next_url(self):
        response = self.test_client.get('/login/?next=%2Fanalyse%2F', follow_redirects=False)
        self.assertEqual(302, response.status_code)
        self.assertIn(b'<a href="/login/spotify">', response.data)

        with self.test_client.session_transaction() as session:
            self.assertEqual('/analyse/', session['next_url'])

        response = self.test_client.get('/', follow_redirects=False)
        self.assertEqual(302, response.status_code)
        self.assertIn(b'<a href="/analyse/">', response.data)

        with self.test_client.session_transaction() as session:
            self.assertNotIn('next_url', session)
