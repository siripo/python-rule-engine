import pytest
from .rule_set_builder import RuleSetBuilder
from .main import ConditionEvaluationContext, Context


def test_pyeval_condition():
    test_rules_csv = """
    id,     rule_id,    rule_desc,      py1,                            py2,                                ##,     action_type,    action_value
    type,   metadata,   metadata,       pyeval,                         pyeval,                             ignore, action_type,    action_arg
    arg,    ,           ,               z=input["a"]+input["b"],        z=cuadrado(input["a"]*input["b"]),  ##,     ,
    arg,    ,           ,               z==cell,                        z in cell,                          ##,     ,
    rule,   r1,         d1,             5,                              "[36]",                             ##,     echo,         chau
    rule,   r2,         d2,             3,                              "[1,16]",                           ##,     echo,         hello
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)

    rule = rule_set.find_rule_by_metadata("rule_id", "r1")

    py1 = rule.condition.get_condition_by_id("py1")
    py2 = rule.condition.get_condition_by_id("py2")

    # Verifico que haga bien la evaluacion de pyeval sin trucos
    ctx = ConditionEvaluationContext(input={"a": 2, "b": 3}, evaluation_ctx={}, global_ctx={})
    ctx.evaluation_set_cache = dict()
    assert py1.evaluate(ctx) == True

    # Verifico que haga mal la evaluacion de pyeval sin trucos
    ctx = ConditionEvaluationContext(input={"a": 2, "b": 2}, evaluation_ctx={}, global_ctx={})
    ctx.evaluation_set_cache = dict()
    assert py1.evaluate(ctx) == False

    def cuadrado(x):
        return x * x

    def cubo(x):
        return x * x * x

    ctx = ConditionEvaluationContext(input={"a": 2, "b": 3}, evaluation_ctx={}, global_ctx={"cuadrado": cuadrado})
    ctx.evaluation_set_cache = dict()
    assert py2.evaluate(ctx) == True

    ctx = ConditionEvaluationContext(input={"a": 2, "b": 3}, evaluation_ctx={}, global_ctx={"cuadrado": cubo})
    ctx.evaluation_set_cache = dict()
    assert py2.evaluate(ctx) == False

    # Verifico que la rule se evalue correctamente sobre toda la entrada
    ctx = ConditionEvaluationContext(input={"a": 2, "b": 3}, evaluation_ctx={}, global_ctx={"cuadrado": cuadrado})
    ctx.evaluation_set_cache = dict()
    assert rule.evaluate(ctx) == True


def test_pyeval_condition_empty_cell():
    test_rules_csv = """
    id,     rule_id,    rule_desc,      py1,                            py2,                                ##,     action_type,    action_value
    type,   metadata,   metadata,       pyeval,                         pyeval,                             ignore, action_type,    action_arg
    arg,    ,           ,               z=input["a"],                   ,                                   ##,     ,
    arg,    ,           ,               cell,                           False,                              ##,     ,
    rule,   r1,         d1,             z,                              True,                               ##,     echo,         chau
    rule,   r2,         "EMPTY CELLS",  ,                               ,                                   ##,     echo,         hello
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)

    rule = rule_set.find_rule_by_metadata("rule_id", "r1")
    py1r1 = rule.condition.get_condition_by_id("py1")
    py2r1 = rule.condition.get_condition_by_id("py2")

    rule = rule_set.find_rule_by_metadata("rule_id", "r2")
    py1r2 = rule.condition.get_condition_by_id("py1")
    py2r2 = rule.condition.get_condition_by_id("py2")

    ctx = ConditionEvaluationContext(input={"a": True}, evaluation_ctx={}, global_ctx={}, evaluation_set_cache={})
    assert py1r1.evaluate(ctx)

    ctx = ConditionEvaluationContext(input={"a": False}, evaluation_ctx={}, global_ctx={}, evaluation_set_cache={})
    assert not py1r1.evaluate(ctx)

    ctx = ConditionEvaluationContext(input={"a": True}, evaluation_ctx={}, global_ctx={}, evaluation_set_cache={})
    assert py1r2.evaluate(ctx)

    ctx = ConditionEvaluationContext(input={"a": False}, evaluation_ctx={}, global_ctx={}, evaluation_set_cache={})
    assert py1r2.evaluate(ctx)

    ctx = ConditionEvaluationContext(input={}, evaluation_ctx={}, global_ctx={}, evaluation_set_cache={})
    assert not py2r1.evaluate(ctx)

    ctx = ConditionEvaluationContext(input={}, evaluation_ctx={}, global_ctx={}, evaluation_set_cache={})
    assert py2r2.evaluate(ctx)


def test_pyeval_rule_set():
    test_rules_csv = """
    id,     rule_id,    rule_desc,      py1,                            py2,                                ##,     action_type,    action_value
    type,   metadata,   metadata,       pyeval,                         pyeval,                             ignore, action_type,    action_arg
    arg,    ,           ,               z=input["a"]*input["b"],        "z=fexe(input['a']-input['b'])",    ##,     ,
    arg,    ,           ,               z==cell,                        "fcmp(z,cell)",                     ##,     ,
    rule,   r1,         d1,             6,                              "[2]",                              ##,     echo,         chau
    rule,   r2,         d2,             20,                             "[16,-16]",                         ##,     echo,         hello
    rule,   r3,         d1,             6,                              "[-2]",                             ##,     echo,         chau2
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)

    rule1 = rule_set.find_rule_by_metadata("rule_id", "r1")
    rule2 = rule_set.find_rule_by_metadata("rule_id", "r2")
    rule3 = rule_set.find_rule_by_metadata("rule_id", "r3")

    def doble(x):
        return x * 2

    def fcmp(z, cell):
        return z in cell

    ctx = Context(input={"a": 3, "b": 2}, evaluation_ctx={}, global_ctx={"fexe": doble, "fcmp": fcmp})
    r = rule_set.evaluate(ctx)
    assert r == rule1

    ctx = Context(input={"a": 10, "b": 2}, evaluation_ctx={}, global_ctx={"fexe": doble, "fcmp": fcmp})
    r = rule_set.evaluate(ctx)
    assert r == rule2

    ctx = Context(input={"a": 2, "b": 10}, evaluation_ctx={}, global_ctx={"fexe": doble, "fcmp": fcmp})
    r = rule_set.evaluate(ctx)
    assert r == rule2

    ctx = Context(input={"a": 2, "b": 3}, evaluation_ctx={}, global_ctx={"fexe": doble, "fcmp": fcmp})
    r = rule_set.evaluate(ctx)
    assert r == rule3

    pass


def test_pyeval_cache():
    test_rules_csv = """
    id,     rule_id,    rule_desc,      py1,                                    py2,                                        ##,     action_type,    action_value
    type,   metadata,   metadata,       pyeval,                                 pyeval,                                     ignore, action_type,    action_arg
    arg,    ,           ,               "z=fe(context,input['a'])",      "z=fe(context,input['a']+1)",        ##,     ,
    arg,    ,           ,               "fp(context,z,cell)",            "fp(context,z,cell-10)",             ##,     ,
    rule,   r1,         d1,             "fc(context,1)",                 "fc(context,12)",                    ##,     echo,         x
    rule,   r2,         d2,             "fc(context,2)",                 "fc(context,13)",                    ##,     echo,         x
    rule,   r3,         d1,             "fc(context,5)",                 "fc(context,99)",                    ##,     echo,         x
    rule,   r4,         d1,             "fc(context,5)",                 "fc(context,16)",                    ##,     echo,         x
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)

    def add_callstrack(ctx, func, arg):
        evctx=ctx.evaluation_ctx
        if "st" not in evctx:
            evctx["st"] = []
        evctx["st"].append(func + str(arg))

    def fe(evctx, x):
        add_callstrack(evctx, "e", x)
        return x

    def fp(evctx, z, cell):
        add_callstrack(evctx, "p", str(z) + "_" + str(cell))
        return z == cell

    def fc(evctx, z):
        add_callstrack(evctx, "c", z)
        return z

    st = []
    ctx = Context(input={"a": 1}, evaluation_ctx={"st": st}, global_ctx={"fe": fe, "fp": fp, "fc": fc})
    r = rule_set.evaluate(ctx)
    assert r != None and r.metadata["rule_id"] == "r1"
    assert st == ['e1', 'c1', 'p1_1', 'e2', 'c12', 'p2_2']

    st = []
    ctx = Context(input={"a": 2}, evaluation_ctx={"st": st}, global_ctx={"fe": fe, "fp": fp, "fc": fc})
    r = rule_set.evaluate(ctx)
    assert r != None and r.metadata["rule_id"] == "r2"
    assert st == ['e2', 'c1', 'p2_1', 'c2', 'p2_2', 'e3', 'c13', 'p3_3']

    st = []
    ctx = Context(input={"a": 5}, evaluation_ctx={"st": st}, global_ctx={"fe": fe, "fp": fp, "fc": fc})
    r = rule_set.evaluate(ctx)
    assert r != None and r.metadata["rule_id"] == "r4"
    assert st == ['e5', 'c1', 'p5_1', 'c2', 'p5_2', 'c5', 'p5_5', 'e6', 'c99', 'p6_89', 'c16', 'p6_6']

    test_rules_csv = """
    id,     rule_id,    rule_desc,      py1,                                    py2,                                        ##,     action_type,    action_value
    type,   metadata,   metadata,       pyeval,                                 pyeval,                                     ignore, action_type,    action_arg
    arg,    ,           ,               "z=fe(context,input['a'])",      "z=fe(context,input['a'])",          ##,     ,
    arg,    ,           ,               "fp(context,z,cell)",            "fp(context,z,cell-10)",             ##,     ,
    rule,   r1,         d1,             "fc(context,1)",                 "fc(context,15)",                    ##,     echo,         x
    rule,   r2,         d2,             "fc(context,1)",                 "fc(context,11)",                    ##,     echo,         x
    """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)
    st = []
    ctx = Context(input={"a": 1}, evaluation_ctx={"st": st}, global_ctx={"fe": fe, "fp": fp, "fc": fc})
    r = rule_set.evaluate(ctx)
    # Pruebo la optimizacion de que el exec cuando es igual use el resultado de uno solo
    assert r != None and r.metadata["rule_id"] == "r2"
    assert st == ['e1', 'c1', 'p1_1', 'c15', 'p1_5', 'c11', 'p1_1']

    test_rules_csv = """
        id,     rule_id,    rule_desc,      py1,                                    py2,                                        ##,     action_type,    action_value
        type,   metadata,   metadata,       pyeval,                                 pyeval,                                     ignore, action_type,    action_arg
        arg,    ,           ,               "z=fe(context,input['a'])",      "z=fe(context,input['a']+22)",       ##,     ,
        arg,    ,           ,               "fp(context,z,cell)",            "fp(context,z,cell-10)",             ##,     ,
        rule,   r1,         d1,             "fc(context,1)",                 "",                                         ##,     echo,         x
        rule,   r2,         d2,             "",                                     "fc(context,37)",                    ##,     echo,         x
        """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)
    # Verifico que la optimizacion del true este funcionando.
    st = []
    ctx = Context(input={"a": 1}, evaluation_ctx={"st": st}, global_ctx={"fe": fe, "fp": fp, "fc": fc})
    r = rule_set.evaluate(ctx)
    assert r != None and r.metadata["rule_id"] == "r1"
    assert st == ['e1', 'c1', 'p1_1']

    # Verifico que la optimizacion del true este funcionando.
    st = []
    ctx = Context(input={"a": 5}, evaluation_ctx={"st": st}, global_ctx={"fe": fe, "fp": fp, "fc": fc})
    r = rule_set.evaluate(ctx)
    assert r != None and r.metadata["rule_id"] == "r2"
    assert st == ['e5', 'c1', 'p5_1', 'e27', 'c37', 'p27_27']

    # Optimizacion cuando el exec, el comparador y la regla son iguales, no debe ejecutarlo
    test_rules_csv = """
            id,     rule_id,    rule_desc,      py1,                             py2,                                        ##,     action_type,    action_value
            type,   metadata,   metadata,       pyeval,                          pyeval,                                     ignore, action_type,    action_arg
            arg,    ,           ,               "z=fe(context,input['a'])",      "z=fe(context,input['a'])",          ##,     ,
            arg,    ,           ,               "fp(context,z,cell)",            "fp(context,z,cell)",                ##,     ,
            rule,   r1,         d1,             "fc(context,1)",                 "fc(context,11)",                    ##,     echo,         x
            rule,   r2,         d2,             "",                              "fc(context,37)",                    ##,     echo,         x
            rule,   r3,         d2,             "fc(context,1)",                 "fc(context,1)",                     ##,     echo,         x
            """

    rule_set = RuleSetBuilder().parse_csv_string(test_rules_csv)
    # Verifico que la optimizacion del true este funcionando.
    st = []
    ctx = Context(input={"a": 1}, evaluation_ctx={"st": st}, global_ctx={"fe": fe, "fp": fp, "fc": fc})
    r = rule_set.evaluate(ctx)
    assert r != None and r.metadata["rule_id"] == "r3"
    assert st == ['e1', 'c1', 'p1_1', 'c11', 'p1_11', 'c37', 'p1_37']
