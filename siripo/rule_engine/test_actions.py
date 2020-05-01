import pytest
from .rule_set_builder import RuleSetBuilder
from .main import ConditionEvaluationContext, Context


def test_action_output():
    test_rules_csv = """
    id,     rule_id,    rule_desc,      py1,                            action_type,    action_value
    type,   metadata,   metadata,       pyeval,                         action_type,    action_arg
    arg,    ,           ,               ,                               ,
    arg,    ,           ,               input['a']==cell,               ,
    rule,   r1,         d1,             1,                              echo,           hola
    rule,   r2,         d2,             2,                              echo,           chau
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)

    ctx = Context(input={"a": 1})
    r = rule_set.evaluate(ctx)
    o = r.action.exec(ctx)
    assert o == "hola"

    ctx = Context(input={"a": 2})
    r = rule_set.evaluate(ctx)
    o = r.action.exec(ctx)
    assert o == "chau"


def test_action_none():
    test_rules_csv = """
    id,     rule_id,    rule_desc,      py1,                            action_type,    action_value
    type,   metadata,   metadata,       pyeval,                         action_type,    action_arg
    arg,    ,           ,               ,                               ,
    arg,    ,           ,               input['a']==cell,               ,
    rule,   r1,         d1,             1,                              none,         hola
    rule,   r2,         d2,             2,                              none,         chau
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)

    ctx = Context(input={"a": 1})
    r = rule_set.evaluate(ctx)
    o = r.action.exec(ctx)
    assert o is None

    ctx = Context(input={"a": 2})
    r = rule_set.evaluate(ctx)
    o = r.action.exec(ctx)
    assert o is None


def test_action_metadata():
    test_rules_csv = """
    id,     rule_id,    rule_desc,      py1,                            action_type,    action_value
    type,   metadata,   metadata,       pyeval,                         action_type,    action_arg
    arg,    ,           ,               ,                               ,
    arg,    ,           ,               input['a']==cell,               ,
    rule,   r1,         d1,             1,                              metadata,         hola
    rule,   r2,         d2,             2,                              metadata,         chau
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)

    ctx = Context(input={"a": 1})
    r = rule_set.evaluate(ctx)
    o = r.action.exec(ctx)
    assert o == {'rule_id': 'r1', 'rule_desc': 'd1', 'action_value': 'hola'}

    ctx = Context(input={"a": 2})
    r = rule_set.evaluate(ctx)
    o = r.action.exec(ctx)
    assert o == {'rule_id': 'r2', 'rule_desc': 'd2', 'action_value': 'chau'}


def test_action_row_dict():
    test_rules_csv = """
    id,     rule_id,    rule_desc,      py1,                            action_type,    action_value
    type,   metadata,   metadata,       pyeval,                         action_type,    action_arg
    arg,    ,           ,               ,                               ,
    arg,    ,           ,               input['a']==cell,               ,
    rule,   r1,         d1,             1,                              row_dict,         hola
    rule,   r2,         d2,             2,                              row_dict,         chau
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)

    ctx = Context(input={"a": 1})
    r = rule_set.evaluate(ctx)
    o = r.action.exec(ctx)
    assert o == {'id': 'rule', 'rule_id': 'r1', 'rule_desc': 'd1', 'py1': '1', 'action_type': 'row_dict', 'action_value': 'hola'}

    ctx = Context(input={"a": 2})
    r = rule_set.evaluate(ctx)
    o = r.action.exec(ctx)
    assert o == {'id': 'rule', 'rule_id': 'r2', 'rule_desc': 'd2', 'py1': '2', 'action_type': 'row_dict', 'action_value': 'chau'}