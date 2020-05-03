import spotipy
import spotipy.util as util


def main():
    token = util.prompt_for_user_token('1121820983', 'user-library-read')
    sp = spotipy.Spotify(auth=token)

    print(sp.audio_features(map(lambda x: x['track']['id'], sp.current_user_saved_tracks()['items'])))


if __name__ == '__main__':
    main()
