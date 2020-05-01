from .main import Condition, ConditionEvaluationContext


class ConditionMultiary(Condition):
    conditions: list
    _conditions_by_id: dict

    def __init__(self):
        self.conditions = list()
        self._conditions_by_id = dict()

    def add_condition(self, condition: Condition, id=None):
        self.conditions.append(condition)
        if id is not None:
            self._conditions_by_id[id] = condition

    def get_condition_by_id(self, id):
        return self._conditions_by_id[id]


class ConditionUnary(Condition):
    condition: Condition


class ConditionAnd(ConditionMultiary):

    def evaluate(self, ctx: ConditionEvaluationContext) -> bool:
        if len(self.conditions) == 0:
            return False
        for c in self.conditions:
            if not c.evaluate(ctx):
                return False
        return True


class ConditionOr(ConditionMultiary):

    def evaluate(self, ctx: ConditionEvaluationContext) -> bool:
        for c in self.conditions:
            if c.evaluate(ctx):
                return True
        return False


class ConditionNot(ConditionUnary):

    def evaluate(self, data, memory: dict = None) -> bool:
        return not self.condition.evaluate(data);


class ConditionTrue(Condition):
    def evaluate(self, data, memory: dict = None) -> bool:
        return True


class ConditionFalse(Condition):
    def evaluate(self, data, memory: dict = None) -> bool:
        return False
