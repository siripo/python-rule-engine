from .rule_set_builder import RuleSetBuilder
from .main import ConditionEvaluationContext, Context


def test_conditions_basic_eq():
    test_rules_csv = """
    id,     rid,        basic
    type,   metadata,   eq
    arg,    ,           "a"
    rule,   r1,         1
    rule,   r2,         2
    rule,   r3,         "'pipi'"
    rule,   r4,         "['q','w',5]"
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)
    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 1}))
    assert rule.metadata["rid"] == "r1"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 2}))
    assert rule.metadata["rid"] == "r2"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": "pipi"}))
    assert rule.metadata["rid"] == "r3"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": "zz"}))
    assert rule is None

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": ["q", "w", 5]}))
    assert rule.metadata["rid"] == "r4"


def test_conditions_basic_any():
    test_rules_csv = """
    id,     rid,        basic
    type,   metadata,   any
    arg,    ,           "a"
    rule,   r1,         "1,2"
    rule,   r2,         "['q','w',5]"
    rule,   r3,         "'a','b'"
    rule,   r4,         "'c'"
    rule,   r5,         
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)
    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 2}))
    assert rule.metadata["rid"] == "r1"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 5}))
    assert rule.metadata["rid"] == "r2"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": "q"}))
    assert rule.metadata["rid"] == "r2"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": "b"}))
    assert rule.metadata["rid"] == "r3"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": "c"}))
    assert rule.metadata["rid"] == "r4"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": "zzzz"}))
    assert rule.metadata["rid"] == "r5"


def test_conditions_basic_gt():
    test_rules_csv = """
    id,     rid,        basic
    type,   metadata,   gt
    arg,    ,           "a"
    rule,   r1,         "100"
    rule,   r2,         "50"
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)
    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 200}))
    assert rule.metadata["rid"] == "r1"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 100}))
    assert rule.metadata["rid"] == "r2"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 60}))
    assert rule.metadata["rid"] == "r2"

    test_rules_csv = """
    id,     rid,        basic
    type,   metadata,   gt
    arg,    ,           "a"
    rule,   r1,         "'q'"
    rule,   r2,         "'b'"
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)
    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": "w"}))
    assert rule.metadata["rid"] == "r1"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": "q"}))
    assert rule.metadata["rid"] == "r2"


def test_conditions_basic_ge():
    test_rules_csv = """
    id,     rid,        basic
    type,   metadata,   ge
    arg,    ,           "a"
    rule,   r1,         "100"
    rule,   r2,         "50"
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)
    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 200}))
    assert rule.metadata["rid"] == "r1"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 100}))
    assert rule.metadata["rid"] == "r1"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 60}))
    assert rule.metadata["rid"] == "r2"

    test_rules_csv = """
    id,     rid,        basic
    type,   metadata,   ge
    arg,    ,           "a"
    rule,   r1,         "'q'"
    rule,   r2,         "'b'"
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)
    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": "w"}))
    assert rule.metadata["rid"] == "r1"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": "q"}))
    assert rule.metadata["rid"] == "r1"


def test_conditions_basic_lt():
    test_rules_csv = """
    id,     rid,        basic
    type,   metadata,   lt
    arg,    ,           "a"
    rule,   r1,         "50"
    rule,   r2,         "100"
    rule,   r3,         
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)
    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 10}))
    assert rule.metadata["rid"] == "r1"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 50}))
    assert rule.metadata["rid"] == "r2"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 60}))
    assert rule.metadata["rid"] == "r2"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 160}))
    assert rule.metadata["rid"] == "r3"


def test_conditions_basic_le():
    test_rules_csv = """
    id,     rid,        basic
    type,   metadata,   le
    arg,    ,           "a"
    rule,   r1,         "50"
    rule,   r2,         "100"
    rule,   r3,         
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)
    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 10}))
    assert rule.metadata["rid"] == "r1"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 50}))
    assert rule.metadata["rid"] == "r1"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 60}))
    assert rule.metadata["rid"] == "r2"

    rule = rule_set.evaluate(ConditionEvaluationContext(input={"a": 160}))
    assert rule.metadata["rid"] == "r3"
