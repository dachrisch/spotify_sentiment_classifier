import json
from logging import config

import spotipy
import spotipy.util as util

from classify.classify import SpotifyMoodClassification


def main():
    with open('app_logging.json') as f:
        config.dictConfig(json.load(f)['logging'])

    # https://developer.spotify.com/documentation/general/guides/scopes/#playlist-modify-private
    token = util.prompt_for_user_token('1121820983', 'user-library-read playlist-modify-private')
    sp = spotipy.Spotify(auth=token)

    SpotifyMoodClassification(sp).analyse()


if __name__ == '__main__':
    main()
