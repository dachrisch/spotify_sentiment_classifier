import json
import unittest
from importlib import resources
from logging import config

from sentiment.classify.classify import FeatureClassifier, RuleHandlerBuilder
from sentiment.classify.sentiment import Sentiment

with resources.open_text('tests', 'tests_logging.json') as f:
    config.dictConfig(json.load(f)['logging'])


class ExtractFeaturesTest(unittest.TestCase):

    def test_classify_single_rule(self):
        expected = Sentiment.BARGAINING
        feature_rule_handler = RuleHandlerBuilder().when('valence', .1, .2).when('danciness', 0, .4).then(
            expected).build()
        feature_classifier = FeatureClassifier(feature_rule_handler)
        self.assertEqual(expected, feature_classifier.classify({'valence': 0.15, 'danciness': 0.3}).name)

    def test_classify_distinct_rules(self):
        expected = Sentiment.ANGER
        feature_rule_handler = RuleHandlerBuilder().when('valence', .1, .2).when(
            'danciness', 0, .4).then(Sentiment.BARGAINING).build()
        feature_rule_handler.set_next(
            RuleHandlerBuilder().when('valence', .2, .3).when('danciness', .4, .6).then(expected).build())
        feature_classifier = FeatureClassifier(feature_rule_handler)
        self.assertEqual(expected, feature_classifier.classify({'valence': 0.25, 'danciness': 0.41}).name)

    def test_first_field_rule_used(self):
        expected = Sentiment.BARGAINING
        feature_rule_handler = RuleHandlerBuilder().when('valence', .1, .2).when('valence', 0, .4).then(
            expected).build()
        feature_classifier = FeatureClassifier(feature_rule_handler)
        self.assertEqual(expected, feature_classifier.classify({'valence': 0.12}).name)

    def test_None_if_outside_of_rule(self):
        expected = Sentiment.BARGAINING
        feature_rule_handler = RuleHandlerBuilder().when('valence', .1, .2).then(expected).build()
        feature_classifier = FeatureClassifier(feature_rule_handler)
        self.assertIsNone(feature_classifier.classify({'valence': 0.5}))


class TestRulesHandler(unittest.TestCase):
    def test_iterate_handler(self):
        handlers = list(RuleHandlerBuilder.default())
        self.assertEqual(len(handlers), len(Sentiment))
        for handler, expected in zip(handlers, Sentiment):
            self.assertEqual(expected, handler.classification.name)
            self.assertIn('valence', map(lambda rule: rule.field, handler.rules))

    def test_rules_handler_from_json(self):
        _json = {'handlers': [
            {'classification': {'name': 'test1'}, 'rules': [{'field': 'valence', 'lower': '.1', 'upper': '.2'}]}
        ]}

        from_json = FeatureClassifier.from_json(_json)
        self.assertEqual('test1', from_json.rule_handler.classification.name)
        field_rule = from_json.rule_handler.rules.pop()
        self.assertEqual('valence', field_rule.field)
        self.assertEqual(.1, field_rule.lower)
        self.assertEqual(.2, field_rule.upper)


class TestDefaultClassification(unittest.TestCase):
    def test_accept_sentiment_enum(self):
        fixture = {
            Sentiment.DEPRESSION: .1,
            Sentiment.ANGER: .3,
            Sentiment.DENIAL: .45,
            Sentiment.BARGAINING: .55,
            Sentiment.ACCEPTANCE: .7,
        }
        for sentiment in Sentiment:
            classification = FeatureClassifier().classify({'valence': fixture[sentiment]})
            self.assertIsNotNone(classification,
                                 'could not classify sentiment {}: {}'.format(sentiment, fixture[sentiment]))
            self.assertEqual(sentiment, classification.name)


if __name__ == '__main__':
    unittest.main()
