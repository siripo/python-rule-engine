from .main import Rule, Action, Context
from .rule_set_builder import RuleBuildContext


class ActionStaticOutput(Action):
    """
    Tipo basico que retorna un output estatico
    """
    _output = None

    def __init__(self, output):
        self._output = output

    def exec(self, ctx: Context):
        return self._output


class ActionNone(ActionStaticOutput):
    """
    Retorna None
    """
    pass


class ActionEcho(ActionStaticOutput):
    """
    Retorna simplemente el string que figura en la columna de tipo action_arg
    """
    pass


class ActionMetadata(ActionStaticOutput):
    """
    Retorna un diccionario con todas las columnas de tipo metadata y action_arg
    """
    pass


class ActionRowDict(ActionStaticOutput):
    """
    Retorna un diccionario con todas las columnas
    """
    pass


class ActionEval(Action):
    """
    Evalua codigo python como respuesta
    """
    _eval_code = None

    def exec(self, ctx: Context):
        exec_ctx = {
            "input": ctx.input,
            "context": ctx
        }
        return eval(self._eval_code, ctx.global_ctx, exec_ctx)


class ActionExec(Action):
    """
    Evalua codigo python como respuesta
    """
    _exec_code = None

    def exec(self, ctx: Context):
        exec_ctx = {
            "input": ctx.input,
            "context": ctx
        }
        exec(self._exec_code, ctx.global_ctx, exec_ctx)
        return exec_ctx["output"]


class ActionRun(Action):
    """
    Evalua otro conjunto de reglas
    """
    _rule_set_id = None

    def exec(self, ctx: Context):
        return ctx.rule_engine.run_with_context(self._rule_set_id, ctx)


def _rule_term_builder_action_type_none(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    return ActionNone(None)


def _rule_term_builder_action_type_echo(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    argid = rule_table['type_index']['action_arg'][0]
    argidx = rule_table['id_index'][argid]
    out = rule_table['rule'][argidx]
    return ActionEcho(out)


def _rule_term_builder_action_type_metadata(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    meta = dict()
    argids: list = []

    if 'metadata' in rule_table['type_index']:
        argids.extend(rule_table['type_index']['metadata'])

    if 'action_arg' in rule_table['type_index']:
        argids.extend(rule_table['type_index']['action_arg'])

    for id in argids:
        idx = rule_table['id_index'][id]
        m = rule_table['rule'][idx]
        meta[id] = m

    return ActionMetadata(meta)


def _rule_term_builder_action_type_row_dict(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    meta = dict()

    for id in rule_table['id_index']:
        idx = rule_table['id_index'][id]
        m = rule_table['rule'][idx]
        meta[id] = m

    return ActionRowDict(meta)


def _rule_term_builder_action_type_eval(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    action = ActionEval()

    argid = rule_table['type_index']['action_arg'][0]
    argidx = rule_table['id_index'][argid]
    evalstr = rule_table['rule'][argidx]
    action._eval_code = compile(evalstr, 'action_eval_' + rule_term["id"], 'eval')

    return action


def _rule_term_builder_action_type_exec(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    action = ActionExec()

    argid = rule_table['type_index']['action_arg'][0]
    argidx = rule_table['id_index'][argid]
    evalstr = rule_table['rule'][argidx]
    action._exec_code = compile(evalstr, 'action_exec_' + rule_term["id"], 'exec')

    return action


def _rule_term_builder_action_type_run(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    action = ActionRun()

    argid = rule_table['type_index']['action_arg'][0]
    argidx = rule_table['id_index'][argid]
    rulesetid = rule_table['rule'][argidx]
    action._rule_set_id = rulesetid

    return action


def rule_term_builders():
    return {
        "action_type_none": _rule_term_builder_action_type_none,
        "action_type_echo": _rule_term_builder_action_type_echo,
        "action_type_metadata": _rule_term_builder_action_type_metadata,
        "action_type_row_dict": _rule_term_builder_action_type_row_dict,
        "action_type_eval": _rule_term_builder_action_type_eval,
        "action_type_exec": _rule_term_builder_action_type_exec,
        "action_type_run": _rule_term_builder_action_type_run,
    }
