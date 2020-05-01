from .main import Rule, RuleSet, Condition, Action
from .conditions import ConditionAnd

"""
Permite leer las reglas desde un csv
la primer columna siempre debe indicar el tipo de fila, los tipos pueden ser:
* id            (obligatorio, unico) para indicar que esa columna se utiliza para los id de columna
* description   (opcional) para indicar que son descripciones de la columna
* ignore        (opcional, multiple) para indicar que la fila debe ser ignorada completamente
* type          (obligatorio, unico) indica de que tipo es la columna
* arg           (opcional, multiple) son argumentos que serán pasados al parser de la rule
* rule          (opcional, multiple) son cada una de las relgas aca va lo util.


En las celdas donde se indica type, el valor puede ser:
* metadata      indica que la columna es de metadatos a ser almacenados en la rule
* pyeval        indica que la columna sera evaluada mediante un pyeval
* action_type   indica que tipo de accion se debe tomar si logro matchear la rule
* action_arg    indica que es un argumento a ser tenido en cuenta al evaluar el action

"""


class RuleBuildContext:
    """
    Es un paquete a ser utilizado durante el building de una rule en las llamadas externas
    """
    # Es el conjunto de builders
    rule_term_builders: dict()

    # Es un paquete key value global para ser utilizado durante el building
    building_cache: dict()

    # El rule set que está en construcción.
    rule_set: RuleSet

    # Algunos builders necesitan paquetes de datos enviados desde afuera, pensar el nombre

    def __init__(self, rule_term_builders: dict(), building_cache: dict(), rule_set: RuleSet):
        self.rule_term_builders = rule_term_builders
        self.building_cache = building_cache
        self.rule_set = rule_set

    def get_cache_namespace(self, name) -> dict:
        if name not in self.building_cache:
            self.building_cache[name] = dict()
        return self.building_cache[name]


class RuleSetBuilder:
    # Conjunto de term builders definidos por el usuario a ser utilizados durante la construccion de terminos de la rule
    rule_term_builders: dict = None

    # Merge de los term builders del usuario si los hubiera y de los default term builders
    _merged_rule_term_builders: dict = None

    # Cache que debe ser generado cuando se construye este builder.
    _building_context_cache: dict = None

    def __init__(self):
        self._building_context_cache = dict()
        self.rule_term_builders = dict()

    def parse_csv_file(self, filename):
        with open(filename, newline='') as csvfile:
            return self.parse_csv_from_ioreader(csvfile)

    def parse_csv_string(self, csv_str):
        import io
        with io.StringIO(csv_str) as csvstr:
            return self.parse_csv_from_ioreader(csvstr)

    def parse_csv_from_ioreader(self, ioreader):
        import csv
        csv_reader = csv.reader(ioreader, delimiter=',', quotechar='\"', skipinitialspace=True)
        return self.parse_using_csv_reader(csv_reader)

    def parse_using_csv_reader(self, csv_reader):
        mat = []
        for row in csv_reader:
            if len(row) == 0:
                continue
            if len(row) == 1:
                if len(str(row[0]).strip()) == 0:
                    continue
            mat.append(row)
        return self.build_rule_set_from_matrix(mat)

    def build_rule_set_from_matrix(self, mat) -> RuleSet:
        table = self._build_table_from_raw_matrix(mat)
        # Mergeo los term builders
        self._merged_rule_term_builders = dict(self._default_rule_term_builders())
        if self.rule_term_builders is not None:
            self._merged_rule_term_builders.update(self.rule_term_builders)
        return self._build_rule_set_from_table(table)

    ######################################################################################################################
    #  PRIVATE STUFF
    ######################################################################################################################

    def _build_rule_set_from_table(self, table) -> RuleSet:
        rule_table = dict(table)

        raw_rules = table["rule"]

        rs = RuleSet()
        for idx, rule_row in enumerate(raw_rules):
            # solo quiero la rule en cuestion
            rule_table["rule"] = rule_row
            # paso el indice de la rule para poder armar ids de cache
            rule_table["rule_index"] = idx
            rule = self._build_rule_from_table(rule_table, rs)
            rs.rules.append(rule)

        return rs

    def _build_table_from_raw_matrix(self, mat):
        # Armo indices de la primer columna, de esta forma facilmente puedo recorrer las rules y los parsers de rules
        table = self._build_row_indexes(mat)
        # Armo los indices por columna y verifico que sean unicos
        table = self._build_column_id_index(table)
        # Armo un indice por tipo
        table = self._build_column_type_index(table)

        # pprint.pprint(table)
        return table

    def _build_row_indexes(self, mat):
        ret = {}

        valid_types = ["id", "description", "type", "arg", "rule"]
        for id in valid_types:
            ret[id] = []

        for row in mat:
            rowtype = str(row[0]).strip()
            if rowtype == "ignore":
                continue
            assert rowtype in valid_types
            ret[rowtype].append(row)

        if len(ret["id"]) == 0:
            # No estaban declarados los ids, los genero aca.
            row = ["id"]
            for x in range(1, len(mat[0])):
                row.append("term_" + str(x))
            ret["id"] = [row]

        assert len(ret["id"]) == 1, "Solo puede haber una row indicando los ids"
        assert len(ret["type"]) == 1, "Debe haber una y solo una row indicando el tipo"

        ret["id"] = ret["id"][0]
        ret["type"] = ret["type"][0]
        return ret

    def _build_column_id_index(self, table):
        """
        armo un indice de columnas por id, en este indice descarto las columnas de tipo ignore
        Ademas verifico que los id sean únicos
        """
        idx = dict()
        for i in range(len(table["id"])):
            if table["type"][i] == "ignore":
                continue
            id = table["id"][i]
            assert id not in idx, f"Los ids deben ser unicos \"{id}\" esta repetido"
            idx[id] = i

        t = dict(table)
        t["id_index"] = idx
        return t

    def _build_column_type_index(self, table):
        """
        Armo un indice por tipo de columna
        Adentro del indice tendré la lista ordenada de izquierda a derecha de todos los ids que tienen ese tipo
        """
        idx = dict()
        for i in range(len(table["type"])):
            if table["type"][i] == "ignore":
                continue
            id = table["id"][i]
            ty = table["type"][i]

            if ty not in idx:
                idx[ty] = []
            idx[ty].append(id)

        t = dict(table)
        t["type_index"] = idx
        return t

    def _build_rule_from_table(self, rule_table, rule_set: RuleSet) -> Rule:
        """
        Intenta construir la rule
        Si viene un rule_set debe ser el set al cual será agregada esta rule, es enviado aqui para permitir optimizar
        """
        rule = Rule()
        rule.condition = ConditionAnd()

        # Genero el id para cache de la rule completa
        rule_table["rule_cache_id"] = "r" + str(rule_table["rule_index"])

        for type, col_ids in rule_table["type_index"].items():
            # El tipo type se utiliza unicamente en la columna que indica que esa row contiene los tipos, debo descartalo
            if type == "type":
                continue
            for col_id in col_ids:
                # Genero la columna para simplificar el laburo al builder que no necesite la tabla
                col = self._build_column_from_rule_table(rule_table, col_id)
                self._call_rule_term_builder(rule_table, rule_set, col, rule)

                pass

        return rule

    def _build_column_from_rule_table(self, rule_table, col_id) -> dict:
        """
        Desde un column id y la rule_table genero el diccionario de la columna para simplificar a builders basicos
        """
        col = {"id": None, "description": [], "type": None, "arg": [], "cell": None}

        # valid_types = ["id", "description", "type", "arg", "rule"]
        idx = rule_table["id_index"][col_id]
        col["id"] = rule_table["id"][idx]
        assert col_id == col["id"]

        col["type"] = rule_table["type"][idx]
        col["cell"] = rule_table["rule"][idx]

        for d in rule_table["description"]:
            col["description"].append(d[idx])

        for d in rule_table["arg"]:
            col["arg"].append(d[idx])

        # Agrego el column index para ser consistente con el rule_index
        col["column_index"] = idx

        # Genero las keys para cache
        col["column_cache_id"] = "c" + str(idx)
        col["cell_cache_id"] = rule_table["rule_cache_id"] + "_" + col["column_cache_id"]

        return col

    def _call_rule_term_builder(self, rule_table, rule_set, rule_term, rule):
        if self._merged_rule_term_builders is None:
            self._merged_rule_term_builders = self._default_rule_term_builders()
        ty = rule_term["type"]
        if not ty in self._merged_rule_term_builders:
            raise Exception(f"No rule term builder of type: \"{ty}\"")
        fn = self._merged_rule_term_builders[ty]

        ctx = RuleBuildContext(rule_term_builders=self._merged_rule_term_builders,
                               building_cache=self._building_context_cache, rule_set=rule_set)

        term = fn(ctx, rule, rule_term, rule_table)
        if term is None:
            return
        if isinstance(term, Condition):
            rule.condition.add_condition(term, rule_term["id"])
        if isinstance(term, Action):
            rule.action = term

    def _default_rule_term_builders(self):
        from .condition_pyeval import rule_term_builders as pyeval_rtb
        from .actions import rule_term_builders as actions_rtb
        from .conditions_basic import rule_term_builders as basic_rtb

        base = {
            "action_arg": _rule_term_builder_action_arg,
            "action_type": _rule_term_builder_action_type,
            "metadata": _rule_term_builder_metadata
        }

        base.update(pyeval_rtb())
        base.update(actions_rtb())
        base.update(basic_rtb())
        return base


######################################################################################################################
#  TERM BUILDERS
######################################################################################################################


def _rule_term_builder_action_arg(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    # Este builder no hace nada
    pass


def _rule_term_builder_action_type(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    ty = "action_type_" + rule_term["cell"]
    if ty not in ctx.rule_term_builders:
        raise Exception(f"No rule term builder of type: \"{ty}\"")
    return ctx.rule_term_builders[ty](ctx, rule, rule_term, rule_table)


def _rule_term_builder_metadata(ctx: RuleBuildContext, rule: Rule, rule_term, rule_table):
    rule.metadata[rule_term["id"]] = rule_term["cell"]
    pass
