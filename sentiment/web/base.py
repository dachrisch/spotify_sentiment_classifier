import logging

from flask import session, g
from flask_dance.contrib.spotify import spotify

from sentiment.web.auth import BeforeRequestDispatcherMixin


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


