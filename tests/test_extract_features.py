import json
import unittest
from importlib import resources
from logging import config

from classify.classify import FeatureClassifier
from classify.sentiment import Sentiment

with resources.open_text('tests', 'tests_logging.json') as f:
    config.dictConfig(json.load(f)['logging'])


class ExtractFeaturesTest(unittest.TestCase):

    def test_classify(self):
        self.assertEqual(Sentiment.BARGAINING, FeatureClassifier().classify({'valence': 0.56}))


if __name__ == '__main__':
    unittest.main()
