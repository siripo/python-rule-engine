import mockito as mk
from .main import RuleSet
from .rule_set_builder import RuleSetBuilder


def test_parse_csv_string_simple_format():
    csv_str = """
    id,1,2
    "qq",     "w'ww",  "aa","zz""rrr"
    """

    expectedmat = [['id', '1', '2'], ['qq', "w'ww", 'aa', 'zz"rrr']]

    def funy(mat):
        assert mat == expectedmat
        return None

    rb = RuleSetBuilder()
    mk.patch(rb.build_rule_set_from_matrix, funy)
    rb.parse_csv_string(csv_str)
    mk.unstub()


def test_build_table_from_raw_matrix():
    test_rules_csv = """
    id,rule_id,rule_description,stm_status,gw_status,action_type,action_value
    type,metadata,metadata,pyeval,pyeval,action_type,action_arg
    arg,,,aa,bb,,
    arg,,,cc,dd,,
    rule,1,Descripcion Opcional,"[“init”, “authorizing”]",autorized,run_sub_machine,sub_machine_id
    """

    def funy(table):
        expected_table = {
            'id': ['id', 'rule_id', 'rule_description', 'stm_status', 'gw_status', 'action_type', 'action_value'],
            'description': [],
            'type': ['type', 'metadata', 'metadata', 'pyeval', 'pyeval', 'action_type', 'action_arg'],
            'arg': [['arg', '', '', 'aa', 'bb', '', ''], ['arg', '', '', 'cc', 'dd', '', '']],
            'rule': [['rule', '1', 'Descripcion Opcional', '[“init”, “authorizing”]', 'autorized', 'run_sub_machine',
                      'sub_machine_id']],
            'id_index': {'id': 0, 'rule_id': 1, 'rule_description': 2, 'stm_status': 3, 'gw_status': 4,
                         'action_type': 5, 'action_value': 6},
            'type_index': {'type': ['id'], 'metadata': ['rule_id', 'rule_description'],
                           'pyeval': ['stm_status', 'gw_status'], 'action_type': ['action_type'],
                           'action_arg': ['action_value']}}

        assert table == expected_table
        return None

    rb = RuleSetBuilder()
    mk.patch(rb._build_rule_set_from_table, funy)
    rb.parse_csv_string(test_rules_csv)
    mk.unstub()


def test_build_rule_from_table():
    table = {'arg': [['arg', '', '', 'A=10', 'z=5', '##', '', ''],
                     ['arg', '', '', 'a==cell', 'b==cell', '##', '', '']],
             'description': [['--', '#rule', 'La descrip', 'comp1', 'comp2', 'ignorar', 'salidatipo', 'salidaval']],
             'id': ['id',
                    'rule_id',
                    'rule_desc',
                    'stat1',
                    'stat2',
                    '##',
                    'action_type',
                    'action_value'],
             'id_index': {'action_type': 6,
                          'action_value': 7,
                          'id': 0,
                          'rule_desc': 2,
                          'rule_id': 1,
                          'stat1': 3,
                          'stat2': 4},
             'rule': ['rule', '2', 'Descripcion de la rule', "'qqq'", '', '##', 'echo', 'hello'],
             'rule_index': 0,
             'type': ['type',
                      'metadata',
                      'metadata',
                      'pyeval',
                      'pyeval',
                      'ignore',
                      'action_type',
                      'action_arg'],
             'type_index': {'action_arg': ['action_value'],
                            'action_type': ['action_type'],
                            'metadata': ['rule_id', 'rule_desc'],
                            'pyeval': ['stat1', 'stat2'],
                            'type': ['id']}}

    rule = RuleSetBuilder()._build_rule_from_table(table, RuleSet())
    # ctx = Context({}, {}, {})
    # print(rule.evaluate(input))
