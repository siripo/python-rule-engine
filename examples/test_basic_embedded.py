from siripo.rule_engine import RuleEngine, RuleSetBuilder

"""
Ejemplo basico de ejecucion desde una tabla embebida.
Este ejemplo ficticio representa las reglas para evaluar si se puede dar credito a una persona
"""

ruleset_csv = """
type,   eq,         any,                        gt,                     action_type,    action_arg
arg,    "name",     "surname",                  "salary.amount",        ,
rule,   ,           "['bigfish','bezos']",      ,                       echo,           black
rule,   "'bin'",    "'laden'",                  ,                       echo,           call police
rule,   ,           ,                           1000,                   echo,           gold
rule,   ,           ,                           100,                    echo,           basic
rule,   ,           ,                           ,                       echo,           no credit
"""


def test_basic_embedded():
    rule_set = RuleSetBuilder().parse_csv_string(ruleset_csv)
    eng = RuleEngine(main_ruleset=rule_set)

    credit = eng.run({"name": "carlos", "surname": "garcia"})
    assert credit == "no credit"

    credit = eng.run({"name": "carlos", "surname": "garcia", "salary": {"amount": 250}})
    assert credit == "basic"

    credit = eng.run({"name": "carlos", "surname": "garcia", "salary": {"amount": 7000}})
    assert credit == "gold"

    credit = eng.run({"name": "carlos", "surname": "bigfish", "salary": {"amount": 7000}})
    assert credit == "black"

    credit = eng.run({"name": "juan", "surname": "bezos", "salary": {"amount": -10}})
    assert credit == "black"

    credit = eng.run({"name": "bin", "surname": "bezos", "salary": {"amount": 982123123}})
    assert credit == "black"

    credit = eng.run({"name": "bin", "surname": "laden", "salary": {"amount": 982123123}})
    assert credit == "call police"
