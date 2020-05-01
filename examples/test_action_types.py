from siripo.rule_engine import RuleEngine, RuleSetBuilder

"""
El objetivo de este ejemplo es mostrar como funcionan algunos de los action types
la regla es super trivial, compara nombres
"""

ruleset_csv = """
id,     ruleid,     cmp1,       acttype,        actarg
type,   metadata,   eq,         action_type,    action_arg
arg,    ,           "name",     ,           
rule,   r1,         'aa',       echo,           pong
rule,   r2,         'bb',       none,
rule,   r3,         'cc',       metadata,       lala
rule,   r4,         'dd',       row_dict,       wowo
rule,   r5,         'ee',       eval,           "5+7"
rule,   r6,         'ff',       exec,           "x=987;output=x;"
rule,   r6,         'gg',       run,            machine2
"""


def test_actions():
    rule_set = RuleSetBuilder().parse_csv_string(ruleset_csv)
    eng = RuleEngine(main_ruleset=rule_set)

    # echo lo que hace es retornar el string tal cual aparece en la columna de tipo action_arg
    output = eng.run({"name": "aa"})
    assert output == "pong"

    # none retorna siempre None
    output = eng.run({"name": "bb"})
    assert output is None

    # metadata retorna todo lo que aparezca en columas de tipo metadata y action_arg, ponendo como id el id de la columna
    output = eng.run({"name": "cc"})
    assert output == {'ruleid': 'r3', 'actarg': 'lala'}

    # row_dict retorna un diccionario con toda la row que machea
    output = eng.run({"name": "dd"})
    assert output == {'id': 'rule', 'ruleid': 'r4', 'cmp1': "'dd'", 'acttype': 'row_dict', 'actarg': 'wowo'}

    # eval evalua lo que aparece en la columna de tipo action_arg y ese es el valor retornado, alli puede evaluar funciones
    output = eng.run({"name": "ee"})
    assert output == 12

    # exec ejecuta el codigo que aparece en action_arg y retorna el valor asignado a output como respuesta
    output = eng.run({"name": "ff"})
    assert output == 987


def test_sub_machine():
    rule_set = RuleSetBuilder().parse_csv_string(ruleset_csv)
    eng = RuleEngine(main_ruleset=rule_set)

    ruleset2_csv = """
    id,     ruleid,     cmp1,       acttype,        actarg
    type,   metadata,   eq,         action_type,    action_arg
    arg,    ,           "name",     ,           
    rule,   r1,         'gg',       echo,           chauuuu
    """
    rule_set2 = RuleSetBuilder().parse_csv_string(ruleset2_csv)
    eng.rulesets["machine2"] = rule_set2

    # run ejecuta otro rule_set identificado con el id que aparece en action_arg
    # en este caso machine2
    # el valor retornado sera el que se determine en machine2
    output = eng.run({"name": "gg"})
    assert output == "chauuuu"
