class Context:
    """
    Representa el contexto a ser pasado para la evaluacion de la maquina
    input es el input que se esta tratando de procesar en este momento
    evaluation_ctx es un contexto compartido para toda la evauacion de un input en particular,
        Es creado por lo menos a nivel de Engine, si no viene pre creado desde afuera.
    global_ctx: Es un contexto que vive mas alla de la evaluacion. Es un medio por ejemplo para que lleguen declaraciones
        de variables o funciones para los pyeval
    """
    input: dict
    evaluation_ctx: dict
    global_ctx: dict

    rule_engine = None
    run_trace = None

    def __init__(self, input=None, evaluation_ctx=None, global_ctx=None):
        self.input = input
        self.evaluation_ctx = evaluation_ctx
        self.global_ctx = global_ctx
        pass


class ConditionEvaluationContext(Context):
    """
    Es un context especifico para ser utilizado durante la evaluacion
    """
    # es un cache utilizado a nivel de evaluacion para un RuleSet durante un input especifico
    # Cuando el contexto cambia a evaluar otro rule_set este cache es recreado
    evaluation_set_cache: dict = None

    def __init__(self, input=None, evaluation_ctx=None, global_ctx=None, evaluation_set_cache=None):
        super(ConditionEvaluationContext, self).__init__(input, evaluation_ctx, global_ctx)
        self.evaluation_set_cache = evaluation_set_cache

    @staticmethod
    def create_from_context(ctx: Context):
        c = ConditionEvaluationContext()
        c.input = ctx.input
        c.global_ctx = ctx.global_ctx
        c.evaluation_ctx = ctx.evaluation_ctx
        c.evaluation_set_cache = dict()
        return c


class Condition:
    """
    Representa la condicion a ser evaluada dentro de una rule
    """

    def evaluate(self, ctx: ConditionEvaluationContext) -> bool:
        return False


class Action:
    """
    Representa una accion a ser ejecutada como resultado del la regla.
    El output del exec del action es lo que retornara el RuleEngine
    """

    def exec(self, ctx: Context):
        return False


class Rule:
    """
    Representa una regla que tiene una condicion a ser evaluada y en el caso que se evaluada correctamente
    action representa la accion a ser ejecutada
    """
    condition: Condition
    action: Action
    metadata: dict

    def __init__(self):
        self.metadata = dict()

    def evaluate(self, ctx: ConditionEvaluationContext) -> bool:
        return self.condition.evaluate(ctx)


class RuleSet:
    """
    Representa un conjunto de reglas.
    Al ejecutar un rule set para un input, se puede optimizar la ejecucion mucho mejor que ejecutando reglas por separado
    """
    rules: list

    def __init__(self):
        self.rules = []

    def evaluate(self, ctxx: Context) -> Rule:
        ctx = ConditionEvaluationContext.create_from_context(ctxx)
        for r in self.rules:
            if r.evaluate(ctx):
                return r
        return None

    def evaluate_all(self, ctxx: Context) -> list:
        ctx = ConditionEvaluationContext.create_from_context(ctxx)
        ret = []
        for r in self.rules:
            if r.evaluate(ctx):
                ret.append(r)
        return ret

    def find_rule_by_metadata(self, meta_id, meta_val):
        for r in self.rules:
            if r.metadata is None:
                continue
            for k, v in r.metadata.items():
                if k == meta_id and v == meta_val:
                    return r
        return None


class RuleEngine:
    """
    Representa el motor capaz de correr de forma optima la evaluacion del/los sets de reglas
    """
    rulesets: dict  # [RuleSet]
    _default_global_context: dict

    def __init__(self, main_ruleset=None):
        self.rulesets = {"main": main_ruleset}
        # aqui deberia cargar funciones default y referencias default
        self._default_global_context = {
            'rule_engine': self,
        }

    # El run sobre el rule engine evalua el set principal.
    # Si obtiene una relga que machea, ejecuta su action
    # Si el action fuese ejecutar recursivamente el rule engine. lo hace.
    def run(self, input: dict, global_ctx: dict = None, evaluation_ctx: dict = None):
        r, trace = self._run(input, global_ctx, evaluation_ctx)
        return r

    def trace(self, input: dict, global_ctx: dict = None, evaluation_ctx: dict = None):
        r, trace = self._run(input, global_ctx, evaluation_ctx)
        return r, trace

    def _run(self, input: dict, global_ctx: dict = None, evaluation_ctx: dict = None):
        gctx = dict(self._default_global_context)
        if global_ctx is not None:
            gctx.update(global_ctx)

        ctx = Context(input, evaluation_ctx=evaluation_ctx, global_ctx=gctx)
        ctx.rule_engine = self
        ctx.run_trace = []
        return self.run_with_context("main", ctx), ctx.run_trace

    def run_with_context(self, rule_set_id, ctx: Context):
        if len(ctx.run_trace) > 100:
            raise Exception("Recursion exceeded")
        if rule_set_id not in self.rulesets:
            raise Exception(f"rule_set {rule_set_id} not found")
        rs = self.rulesets[rule_set_id]
        r = rs.evaluate(ctx)

        ctx.run_trace.append((rule_set_id, r))

        if r is None:
            return None
        return r.action.exec(ctx)
