from .rule_set_builder import RuleBuildContext
from .main import Rule, Condition, ConditionEvaluationContext
from .conditions import ConditionTrue


class ConditionPyEval(Condition):
    _exec_code = None
    _compare_code = None
    _cell_code = None

    _exec_cache_id = None
    _eval_cache_id = None

    def evaluate(self, ctx: ConditionEvaluationContext) -> bool:
        # Si ya tengo calculada la salida la utilizo
        if self._eval_cache_id in ctx.evaluation_set_cache:
            return ctx.evaluation_set_cache[self._eval_cache_id]

        # determino si ya tengo pre calculada la salida de exec, la cual es cacheable en el contexto de evaluation ctx
        exec_output_ctx = ctx.evaluation_set_cache.get(self._exec_cache_id, None)
        if exec_output_ctx is None:
            # No la tengo cacheada, tento que calcularla
            exec_ctx = {
                "input": ctx.input,
                "context": ctx
            }
            exec(self._exec_code, ctx.global_ctx, exec_ctx)
            exec_output_ctx = exec_ctx
            ctx.evaluation_set_cache[self._exec_cache_id] = exec_output_ctx

        cell_ctx = exec_output_ctx

        cell_ret = eval(self._cell_code, ctx.global_ctx, cell_ctx)

        cmp_ctx = dict(cell_ctx)
        cmp_ctx["cell"] = cell_ret

        ret = eval(self._compare_code, ctx.global_ctx, cmp_ctx)

        # Agrego la salida al cache
        ctx.evaluation_set_cache[self._eval_cache_id] = ret
        return ret


def _rule_term_builder_pyeval(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    if str(rule_term["cell"]).strip() == "":
        # En el caso de una condition que evalua siempre como true retorno un true directamente
        return ConditionTrue()

    cond = ConditionPyEval()

    cond._exec_code = compile(rule_term["arg"][0], 'pyeval_exec_' + rule_term["id"], 'exec')
    cond._compare_code = compile(rule_term["arg"][1], 'pyeval_cmp_' + rule_term["id"], 'eval')
    cond._cell_code = compile(rule_term["cell"], 'pyeval_cell_' + rule_term["id"], 'eval')

    cond._exec_cache_id = rule_term["cell_cache_id"] + "_exec"
    cond._eval_cache_id = rule_term["cell_cache_id"] + "_eval"

    # Ahora optimizo reduciendo memoria y facilitando el uso de cache.
    cache = ctx.get_cache_namespace(__name__)

    # Optimizo el exec, buscando en alguna rule anterior que tenga este codigo
    if cond._exec_code in cache:
        c = cache[cond._exec_code]
        cond._exec_code = c._exec_code
        # si el codigo es exactamente igual, entonces puedo utilizar el mismo id de cache
        cond._exec_cache_id = c._exec_cache_id
    else:
        cache[cond._exec_code] = cond

    # Optimizo la memoria para el comparador reutilizando codigo igual
    if cond._compare_code in cache:
        c = cache[cond._compare_code]
        cond._compare_code = c._compare_code
    else:
        cache[cond._compare_code] = cond

    # Optimizo la memoria para la celda reutilizando codigo igual
    if cond._cell_code in cache:
        c = cache[cond._cell_code]
        cond._cell_code = c._cell_code
    else:
        cache[cond._cell_code] = cond

    # Optimizo el cache de la celda cuando es identica
    cellcachekey = (cond._exec_code, cond._compare_code, cond._cell_code)
    if cellcachekey in cache:
        c = cache[cellcachekey]
        cond._eval_cache_id = c._eval_cache_id
    else:
        cache[cellcachekey] = cond

    return cond


def rule_term_builders():
    return {
        "pyeval": _rule_term_builder_pyeval
    }
