from enum import Enum


class Sentiment(Enum):
    def __new__(cls, index, playlist):
        obj = object.__new__(cls)
        obj._value_ = index
        obj.playlist = playlist
        return obj

    DEPRESSION = 1, 'gm_mood_1'
    ANGER = 2, 'gm_mood_2'
    DENIAL = 3, 'gm_mood_3'
    BARGAINING = 4, 'gm_mood_4'
    ACCEPTANCE = 5, 'gm_mood_5'
