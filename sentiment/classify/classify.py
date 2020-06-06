from abc import ABC, abstractmethod
from typing import Any, Set

from sentiment.classify.sentiment import Sentiment


class RuleHandler(ABC):
    def __init__(self):
        self.next_handler: RuleHandler = None

    def set_next(self, next_handler):
        self.next_handler = next_handler
        return self.next_handler

    def handle(self, request: Any):
        handled = None
        if self._accept(request):
            handled = self._process(request)
        elif self.next_handler:
            handled = self.next_handler.handle(request)
        return handled

    @abstractmethod
    def _accept(self, request):
        raise NotImplementedError

    @abstractmethod
    def _process(self, request):
        raise NotImplementedError


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


class FieldRule(object):
    def __init__(self, field, lower, upper):
        self.field = field
        self.lower = lower
        self.upper = upper

    def validate(self, request):
        return self.field in request and self.lower <= request[self.field] <= self.upper

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
        return all(rule.validate(request) for rule in self.rules)

    def when(self, field: str, lower: float, upper: float):
        self.rules.add(FieldRule(field, lower, upper))
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


class DefaultHandlerBuilder(object):
    @classmethod
    def build(cls) -> FeatureRuleHandler:
        chain = FeatureRuleHandler(Classification(Sentiment.DEPRESSION))
        chain.when('valence', 0, .2). \
            set_next(FeatureRuleHandler(Classification(Sentiment.ANGER)).when('valence', 0.2, .4)). \
            set_next(FeatureRuleHandler(Classification(Sentiment.DENIAL)).when('valence', 0.4, .5)). \
            set_next(FeatureRuleHandler(Classification(Sentiment.BARGAINING)).when('valence', 0.5, .6)). \
            set_next(FeatureRuleHandler(Classification(Sentiment.ACCEPTANCE)).when('valence', 0.6, 1))
        return chain


class FeatureClassifier(object):
    def __init__(self, rule_handler=DefaultHandlerBuilder.build()):
        self.rule_handler = rule_handler

    def classify(self, track_feature):
        return self.rule_handler.handle(track_feature)

    @classmethod
    def from_json(cls, json):
        chain = None
        _next = None
        for handler in json['handlers']:
            _next = FeatureRuleHandler(Classification(handler['classification']['name']))
            if chain:
                chain.set_next(_next)
            else:
                chain = _next
            for rule in handler['rules']:
                _next.when(rule['field'], float(rule['lower']), float(rule['upper']))
            _next = chain
        return cls(chain)
