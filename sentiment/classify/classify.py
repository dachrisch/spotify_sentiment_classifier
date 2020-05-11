from sentiment.classify.sentiment import Sentiment


class FeatureClassifier(object):

    @staticmethod
    def classify(track_feature):
        valence = track_feature['valence']
        if 0 <= valence < .2:
            return Sentiment.DEPRESSION
        elif .2 <= valence < .4:
            return Sentiment.ANGER
        elif .4 <= valence < .5:
            return Sentiment.DENIAL
        elif .5 <= valence < .6:
            return Sentiment.BARGAINING
        elif .6 <= valence <= 1:
            return Sentiment.ACCEPTANCE


