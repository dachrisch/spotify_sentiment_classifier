from abc import ABC, abstractmethod
from typing import Any, Set, List

from sentiment.classify.sentiment import Sentiment


class Classification(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Classification({:s})'.format(self.name)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return other and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)


class RuleHandler(ABC):
    def __init__(self):
        self.next_handler: RuleHandler = None

    def set_next(self, next_handler):
        self.next_handler = next_handler
        return self.next_handler

    def handle(self, request: Any) -> Classification:
        handled = None
        if self._accept(request):
            handled = self._process(request)
        elif self.next_handler:
            handled = self.next_handler.handle(request)
        return handled

    @abstractmethod
    def _accept(self, request) -> bool:
        raise NotImplementedError

    @abstractmethod
    def _process(self, request):
        raise NotImplementedError


class FieldRule(object):
    def __init__(self, field, lower, upper):
        self.field = field
        self.lower = lower
        self.upper = upper

    def accept(self, request):
        return self.field in request

    def validate(self, request):
        return self.lower <= request[self.field] <= self.upper

    def __hash__(self):
        return hash(self.field)

    def __eq__(self, other):
        return other and self.field == other.field

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '{me}({lower}<={field}<={upper})'.format(me=self.__class__.__name__, lower=self.lower, upper=self.upper,
                                                        field=self.field)


class FeatureRuleHandler(RuleHandler):
    def __init__(self, classification: Classification):
        super().__init__()
        self.rules: Set[FieldRule] = set()
        self.classification: Classification = classification

    def _process(self, request: Any) -> Classification:
        return self.classification

    def _accept(self, request: Any) -> bool:
        return all(rule.validate(request) for rule in filter(lambda rule: rule.accept(request), self.rules))

    def when(self, field_rule: FieldRule):
        self.rules.add(field_rule)
        return self

    def __iter__(self):
        return RuleIterator(self)

    def __repr__(self):
        return '{me}(classification={classification}, rules={rules})'.format(me=self.__class__.__name__,
                                                                             classification=self.classification,
                                                                             rules=self.rules)


class RuleIterator(object):
    def __init__(self, rule_handler: RuleHandler):
        self.next = rule_handler

    def __next__(self):
        current = self.next
        if not current:
            raise StopIteration
        self.next = current.next_handler
        return current


class RuleHandlerBuilder(object):
    def __init__(self):
        self.rule_handlers: List[RuleHandler] = []
        self.rules: List[FieldRule] = []

    @classmethod
    def default(cls) -> RuleHandler:
        builder = RuleHandlerBuilder()
        builder.when('valence', 0, .2).when('danceability', 0, 1). \
            when('energy', 0, 1). \
            when('key', 0, 1). \
            when('loudness', 0, 1). \
            when('mode', 0, 1). \
            when('speechiness', 0, 1). \
            when('acousticness', 0, 1). \
            when('instrumentalness', 0, 1). \
            when('liveness', 0, 1). \
            when('tempo', 0, 1).then(Sentiment.DEPRESSION)
        builder.when('valence', 0.2, .4).then(Sentiment.ANGER)
        builder.when('valence', 0.4, .5).then(Sentiment.DENIAL)
        builder.when('valence', 0.5, .6).then(Sentiment.BARGAINING)
        builder.when('valence', 0.6, 1).then(Sentiment.ACCEPTANCE)
        return builder.build()

    def when(self, field: str, lower: float, upper: float):
        self.rules.append(FieldRule(field, lower, upper))
        return self

    def then(self, classification_name):
        feature_rule_handler = FeatureRuleHandler(Classification(classification_name))
        self.rule_handlers.append(feature_rule_handler)
        for rule in self.rules:
            feature_rule_handler.when(rule)
        self.rules.clear()

        return self

    def build(self) -> RuleHandler:
        self.rule_handlers.reverse()
        current_rule = rule_chain = self.rule_handlers.pop()
        while self.rule_handlers:
            next_handler = self.rule_handlers.pop()
            current_rule.set_next(next_handler)
            current_rule = next_handler
        return rule_chain


class FeatureClassifier(object):
    def __init__(self, rule_handler=RuleHandlerBuilder.default()):
        self.rule_handler = rule_handler

    def classify(self, track_feature) -> Classification:
        return self.rule_handler.handle(track_feature)

    @classmethod
    def from_json(cls, json):
        builder = RuleHandlerBuilder()
        for handler in json['handlers']:
            for rule in handler['rules']:
                builder.when(rule['field'], float(rule['lower']), float(rule['upper'])).then(
                    handler['classification']['name'])
        return cls(builder.build())
