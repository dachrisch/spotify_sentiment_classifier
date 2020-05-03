import logging
import sys
from functools import partial

import spotipy

from classify.sentiment import Sentiment
from spotify.playlist import PlaylistManager


def all_items(limited_call):
    initial_result = limited_call()
    limit = initial_result['limit']
    total = initial_result['total']
    offset = initial_result['offset']

    print(initial_result['href'])

    if offset + len(initial_result['items']) + 1 < total:
        next_results = all_items(partial(limited_call, offset=offset + limit))
        return initial_result['items'] + next_results
    else:
        return initial_result['items']


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    token = spotipy.util.prompt_for_user_token('1121820983', 'playlist-modify-private playlist-read-private')
    sp = spotipy.Spotify(auth=token)

    for playlist in all_items(sp.current_user_playlists):
        if playlist['name'] in (PlaylistManager._to_playlist(sentiment) for sentiment in Sentiment):
            print('delete %s' % playlist)
            sp.user_playlist_unfollow('1121820983', playlist['id'])
