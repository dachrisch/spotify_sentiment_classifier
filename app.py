import logging
import sys

import spotipy
import spotipy.util as util

from classify.classify import SpotifyMoodClassification, FeatureClassifier


def main():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # https://developer.spotify.com/documentation/general/guides/scopes/#playlist-modify-private
    token = util.prompt_for_user_token('1121820983', 'user-library-read playlist-modify-private')
    sp = spotipy.Spotify(auth=token)

    SpotifyMoodClassification(sp, FeatureClassifier()).perform()


if __name__ == '__main__':
    main()
