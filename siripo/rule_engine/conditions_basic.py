from .rule_set_builder import RuleBuildContext
from .main import Rule, Condition, ConditionEvaluationContext
from .conditions import ConditionTrue
from jsonpath_ng import parse


# https://github.com/h2non/jsonpath-ng
# https://jsonpath.com/

class ConditionBasicBase(Condition):
    _find_exp = None
    _parsed_find_exp = None
    _parsed_cell_value = None

    _find_cache_id = None

    def evaluate(self, ctx: ConditionEvaluationContext) -> bool:
        if self._find_cache_id in ctx.evaluation_set_cache:
            fv = ctx.evaluation_set_cache[self._find_cache_id]
        else:
            f = self._parsed_find_exp.find(ctx.input)
            if f is not None and len(f) >= 1:
                fv = f[0].value
            else:
                fv = None
            ctx.evaluation_set_cache[self._find_cache_id] = fv

        return self._cmp(fv, self._parsed_cell_value)

    def _cmp(self, a, b):
        raise NotImplementedError()


class ConditionBasicEq(ConditionBasicBase):
    def _cmp(self, a, b):
        return a == b


class ConditionBasicAny(ConditionBasicBase):
    def _cmp(self, a, b):
        return a in b


class ConditionBasicGt(ConditionBasicBase):
    def _cmp(self, a, b):
        if a is None:
            return False
        return a > b


class ConditionBasicGe(ConditionBasicBase):
    def _cmp(self, a, b):
        if a is None:
            return False
        return a >= b


class ConditionBasicLt(ConditionBasicBase):
    def _cmp(self, a, b):
        if a is None:
            return False
        return a < b


class ConditionBasicLe(ConditionBasicBase):
    def _cmp(self, a, b):
        if a is None:
            return False
        return a <= b


def _rule_term_builder_basic(cond: ConditionBasicBase, ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    if str(rule_term["cell"]).strip() == "":
        return ConditionTrue()
    cond._find_exp = rule_term["arg"][0]
    cond._parsed_find_exp = parse(cond._find_exp)
    cond._parsed_cell_value = eval(rule_term["cell"], {}, {})

    cond._find_cache_id = rule_term["cell_cache_id"] + "_find"

    # Ahora optimizo
    cache = ctx.get_cache_namespace(__name__)
    # Optimizo cache al utilizar el mismo id, y memoria utilizando la misma parsed expression
    if cond._find_exp in cache:
        cond._find_cache_id = cache[cond._find_exp]._find_cache_id
        cond._parsed_find_exp = cache[cond._find_exp]._parsed_find_exp
    else:
        cache[cond._find_exp] = cond

    return cond


def _rule_term_builder_eq(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    return _rule_term_builder_basic(ConditionBasicEq(), ctx, rule, rule_term, rule_table)


def _rule_term_builder_any(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    cond = _rule_term_builder_basic(ConditionBasicAny(), ctx, rule, rule_term, rule_table)
    if not isinstance(cond, ConditionBasicBase):
        return cond
    if type(cond._parsed_cell_value) is tuple:
        cond._parsed_cell_value = list(cond._parsed_cell_value)
    if not type(cond._parsed_cell_value) is list:
        cond._parsed_cell_value = [cond._parsed_cell_value]
    return cond


def _rule_term_builder_gt(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    return _rule_term_builder_basic(ConditionBasicGt(), ctx, rule, rule_term, rule_table)


def _rule_term_builder_ge(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    return _rule_term_builder_basic(ConditionBasicGe(), ctx, rule, rule_term, rule_table)


def _rule_term_builder_lt(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    return _rule_term_builder_basic(ConditionBasicLt(), ctx, rule, rule_term, rule_table)


def _rule_term_builder_le(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    return _rule_term_builder_basic(ConditionBasicLe(), ctx, rule, rule_term, rule_table)


def rule_term_builders():
    return {
        "eq": _rule_term_builder_eq,
        "any": _rule_term_builder_any,
        "gt": _rule_term_builder_gt,
        "ge": _rule_term_builder_ge,
        "lt": _rule_term_builder_lt,
        "le": _rule_term_builder_le,
    }
