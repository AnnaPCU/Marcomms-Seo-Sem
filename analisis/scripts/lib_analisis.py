# -*- coding: utf-8 -*-
"""
lib_analisis.py — funciones compartidas por el análisis y la verificación.

Coincidencia por TEMA (CLAUDE.md §6): tokens de 3+ caracteres, sin acentos, sin
stopwords ni palabras genéricas. Un término de Ads "cubre" una query de GSC cuando
todos los tokens-tema del término aparecen en la query (tras normalizar).
"""
import os, re, unicodedata
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST = os.path.join(ROOT, "datos", "gsc-historico")
BASE = os.path.join(ROOT, "datos", "gsc")
ADS = os.path.join(ROOT, "datos", "ads")

VENTANA_ADS = ("2026-08-01", "2026-09-11")
VENTANA_12M = ("2025-09-15", "2026-09-12")

# ---------------------------------------------------------------- normalización
STOP = set("""
de del la el los las un una unos unas y o e u a en con por para sin sobre entre
que qué como cómo cual cuál cuales cuáles donde dónde cuando cuándo es son ser
al lo le les se su sus mi mis tu tus nos nuestro nuestra más menos muy hay
the of and or for in on at to by with from is are be as an a this that what how
which where when who why does do it its into get become need near best top free
cost price mean means meaning your you my we our
da do das dos na no nas nos em um uma uns umas com por para sem sobre entre que
como qual quais onde quando é são ser ao à às aos o os as e ou
""".split())

GENERICAS = set("""
certificacion certificaciones certificado certificados certificar certificarse
certificacao certificacoes certification certifications certificate certificates
certified certify certifying certifier certifiers certifying
auditoria auditorias auditor auditores audit audits auditing auditors
norma normas standard standards estandar estandares padrao
empresa empresas company companies servicio servicios service services
sistema sistemas system systems gestion gestao management
requisitos requisito requirements requirement proceso procesos process
obtener conseguir sacar como que significa precio costo cuanto cuesta
online gratis curso cursos course courses training capacitacion
argentina españa espana spain portugal canada canadá mexico méxico chile peru perú
brasil brazil usa estados unidos united states america latam europa europe
control union controlunion peterson solutions iso
""".split())

_tok_re = re.compile(r"[a-z0-9][a-z0-9+\.]*")


def sin_acentos(s):
    return "".join(c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c))


def normalizar(s):
    s = sin_acentos(s).lower()
    s = s.replace("-", " ").replace("_", " ").replace("/", " ")
    s = re.sub(r"[\"\[\]'“”]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def stem(t):
    """stemming mínimo es/pt/en: quita plural simple"""
    t = t.rstrip(".")
    if len(t) <= 4 or any(ch.isdigit() for ch in t):
        return t                      # siglas y números de norma no se tocan
    if len(t) > 4 and t.endswith("es") and not t.endswith("ies"):
        t = t[:-2]
    elif len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
        t = t[:-1]
    return t


def tokens_tema(s):
    """tokens de 3+ caracteres, sin stopwords ni genéricas, stemmeados; también
    conserva números de norma tipo 27001, 45001, 22000, 9001 (>=3 dígitos)"""
    out = []
    for t in _tok_re.findall(normalizar(s)):
        base = t.rstrip(".")
        if base in STOP or base in GENERICAS:
            continue
        if len(base) < 3 and not base.isdigit():
            continue
        st = stem(base)
        if st in GENERICAS:
            continue
        out.append(st)
    return tuple(dict.fromkeys(out))          # sin duplicados, orden estable


# ---------------------------------------------------------------- carga GSC

def cargar_hist(marca, corte):
    p = os.path.join(HIST, marca, f"gsc_{marca}_hist_{corte}.csv")
    return pd.read_csv(p, encoding="utf-8-sig", dtype={"query": str, "page": str})


def cargar_base(marca, ventana, corte):
    p = os.path.join(BASE, f"gsc_{marca}_{ventana}_{corte}.csv")
    return pd.read_csv(p, encoding="utf-8-sig", dtype={"query": str, "page": str})


def agregar(df, claves):
    """suma clics e impresiones, recalcula ctr y posición ponderada por impresiones"""
    g = df.assign(_pw=df["position"] * df["impressions"]).groupby(claves, as_index=False).agg(
        clicks=("clicks", "sum"), impressions=("impressions", "sum"), _pw=("_pw", "sum"))
    g["ctr"] = (g["clicks"] / g["impressions"]).where(g["impressions"] > 0, 0).round(6)
    g["position"] = (g["_pw"] / g["impressions"]).where(g["impressions"] > 0, 0).round(2)
    return g.drop(columns="_pw")


# ---------------------------------------------------------------- carga Ads

def _num(s):
    if pd.isna(s):
        return 0.0
    s = str(s).strip()
    if s in ("--", ""):
        return 0.0
    s = s.replace("%", "").replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def _num_int(s):
    if pd.isna(s):
        return 0
    s = str(s).strip().replace(".", "")
    return int(s) if s.isdigit() else 0


def cargar_terminos():
    df = pd.read_csv(os.path.join(ADS, "Informe de terminos de busqueda.csv"),
                     skiprows=2, encoding="utf-8", dtype=str)
    df = df[df["Campaña"].notna()].copy()
    df = df.rename(columns={"Término de búsqueda": "termino", "Campaña": "campana",
                            "Grupo de anuncios": "grupo_anuncios", "Tipo de concordancia": "concordancia",
                            "Añadido/excluido": "estado"})
    df["clics"] = df["Clics"].map(_num_int)
    df["impr"] = df["Impr."].map(_num_int)
    df["coste"] = df["Coste"].map(_num)
    df["conv"] = df["Conversiones"].map(_num)
    df["termino_n"] = df["termino"].map(normalizar)
    df["tema"] = df["termino"].map(tokens_tema)
    df = df.join(df["campana"].map(campana_meta).apply(pd.Series))
    return df[["termino", "termino_n", "tema", "campana", "grupo_anuncios", "concordancia", "estado",
               "clics", "impr", "coste", "conv", "marca", "propiedad", "pais", "camp_corta"]]


def cargar_keywords():
    df = pd.read_csv(os.path.join(ADS, "Informe de palabras clave de busqueda.csv"),
                     skiprows=2, encoding="utf-8", dtype=str)
    df = df[df["Campaña"].notna()].copy()
    df = df.rename(columns={"Palabra clave": "keyword", "Campaña": "campana",
                            "Grupo de anuncios": "grupo_anuncios", "Tipo de concordancia": "concordancia",
                            "URL final": "url_final", "Estado": "estado_kw"})
    df["clics"] = df["Interacciones"].map(_num_int)
    df["impr"] = df["Impr."].map(_num_int)
    df["coste"] = df["Coste"].map(_num)
    df["conv"] = df["Conversiones"].map(_num)
    df["keyword_n"] = df["keyword"].map(normalizar)
    df["tema"] = df["keyword"].map(tokens_tema)
    df = df.join(df["campana"].map(campana_meta).apply(pd.Series))
    return df[["keyword", "keyword_n", "tema", "campana", "grupo_anuncios", "concordancia", "estado_kw",
               "url_final", "clics", "impr", "coste", "conv", "marca", "propiedad", "pais", "camp_corta"]]


def campana_meta(c):
    c = str(c)
    if c.startswith("CU España"):
        m = dict(marca="CU", propiedad="España", pais="esp")
    elif c.startswith("CU Portugal"):
        m = dict(marca="CU", propiedad="Portugal", pais="prt")
    elif c.startswith("CU Canada"):
        m = dict(marca="CU", propiedad="Norteamérica", pais="can")
    elif c.startswith("CU United States"):
        m = dict(marca="CU", propiedad="Norteamérica", pais="usa")
    elif c.startswith("CU Argentina"):
        m = dict(marca="CU", propiedad="Argentina", pais="arg")
    elif re.match(r"^CU_(US|CA)_", c):  # naming estándar: CU_US_SEARCH_GPFS-2026_EN
        m = dict(marca="CU", propiedad="Norteamérica", pais="usa" if c[3:5] == "US" else "can")
    elif c.startswith("CU_AR_"):
        m = dict(marca="CU", propiedad="Argentina", pais="arg")
    elif c.startswith("CU_ES_"):
        m = dict(marca="CU", propiedad="España", pais="esp")
    elif c.startswith("CU_PT_"):
        m = dict(marca="CU", propiedad="Portugal", pais="prt")
    elif c.startswith("PS_AR_"):
        m = dict(marca="PS", propiedad="Américas", pais="arg")
    elif c.startswith("PS Argentina"):
        m = dict(marca="PS", propiedad="Américas", pais="arg")
    else:
        m = dict(marca="?", propiedad="?", pais="?")
    corta = re.sub(r"\s*-?\s*search\s*$", "", c, flags=re.I)
    corta = re.sub(r"^(CU|PS) (España|Portugal|Canada|United States|Argentina)\s*-?\s*", "", corta)
    corta = re.sub(r"^(SuSo|SuSe)\s*-\s*", "", corta)
    corta = re.sub(r"^Organic\s*-\s*", "", corta).strip(" -")
    m["camp_corta"] = corta
    return m


# ---------------------------------------------------------------- normas / temas

NORMAS = [
    # (etiqueta, regex sobre query normalizada)
    ("ISO 45001", r"\b45001\b"),
    ("ISO 27001", r"\b27001\b"),
    ("ISO 9001", r"\b9001\b"),
    ("ISO 14001", r"\b14001\b"),
    ("ISO 22000", r"\biso ?22000\b"),
    ("FSSC 22000", r"\bfssc\b"),
    ("BRCGS", r"\bbrc(gs)?\b"),
    ("IFS", r"\bifs\b"),
    ("GMP+", r"\bgmp ?\+|\bgmp plus\b|\bgmp\b"),
    ("FSC", r"\bfsc\b"),
    ("PEFC", r"\bpefc\b"),
    ("GOTS", r"\bgots\b"),
    ("GRS", r"\bgrs\b|global recycled"),
    ("OEKO-TEX", r"oeko|okotex|oko tex"),
    ("RecyClass", r"recyclass|15343"),
    ("ISCC", r"\biscc\b"),
    ("2BSvs", r"2bs"),
    ("SURE", r"\bsure\b"),
    ("SBP", r"\bsbp\b"),
    ("RED II/III", r"\bred (ii|iii)\b|red ii\b"),
    ("SMETA / Sedex", r"\bsmeta\b|\bsedex\b"),
    ("RSPO", r"\brspo\b"),
    ("RTRS", r"\brtrs\b"),
    ("Rainforest Alliance", r"rainforest|\bra certif"),
    ("GLOBALG.A.P.", r"global ?g\.?a\.?p|globalgap|\bggap\b|\bgrasp\b"),
    ("PrimusGFS", r"primus"),
    ("CanadaGAP", r"canada ?gap"),
    ("USDA NOP / orgánico", r"\bnop\b|\busda\b|organic|organico|organica|ecologic"),
    ("MSC / ASC / BAP", r"\bmsc\b|\basc\b|\bbap\b|aquaculture|acuicultura|aquacultura"),
    ("FSA", r"\bfsa\b"),
    ("FSMA", r"\bfsma\b"),
    ("Welfair / bienestar animal", r"welfair|bienestar animal"),
    ("Halal", r"halal"),
    ("Kosher", r"kosher"),
    ("VISEC", r"visec"),
    ("TEMO", r"\btemo\b"),
    ("CUMCS", r"cumcs"),
    ("FSLM / Higg", r"\bfslm\b|\bhigg\b"),
    ("EUDR", r"eudr|deforest"),
    ("CSRD", r"\bcsrd\b"),
    ("CBAM", r"\bcbam\b"),
    ("GRI / ESG", r"\bgri\b|\besg\b"),
    ("Huella de carbono / GEI", r"huella de carbono|carbon footprint|\bgei\b|14064|14067|efecto invernadero"),
    ("Huella hídrica", r"huella h[ií]drica|huella de agua|14046"),
    ("CAE", r"\bcae\b|\bcaes\b|ahorro energ"),
    ("Agricultura regenerativa", r"regenerativ"),
    ("Bioenergía / biomasa", r"bioenerg|biomas|biog[aá]s|biocombust"),
]


def etiquetar_norma(q):
    qn = normalizar(q)
    for et, rx in NORMAS:
        if re.search(rx, qn):
            return et
    return None


# ---------------------------------------------------------------- cobertura por tema

class IndiceTema:
    """Índice de queries de GSC por token-tema, para medir presencia orgánica de un tema."""

    def __init__(self, df_queries):
        # df_queries: query, impressions, clicks, position (ya agregado por query)
        self.df = df_queries.reset_index(drop=True)
        self.df["_tema"] = self.df["query"].map(tokens_tema)
        self.por_query = dict(zip(self.df["query"].map(normalizar), self.df.index))
        self.idx = {}
        for i, toks in enumerate(self.df["_tema"]):
            for t in toks:
                self.idx.setdefault(t, set()).add(i)

    def presencia(self, tema):
        """filas de GSC cuyas queries contienen TODOS los tokens-tema dados"""
        if not tema:
            return self.df.iloc[0:0]
        sets = [self.idx.get(t, set()) for t in tema]
        ids = set.intersection(*sets) if sets else set()
        return self.df.loc[sorted(ids)]

    def exacta(self, texto):
        i = self.por_query.get(normalizar(texto))
        return None if i is None else self.df.loc[i]

    def clasificar(self, texto, umbral_fuerte=200):
        """devuelve (grupo, impresiones_tema, fila_exacta)"""
        ex = self.exacta(texto)
        tema = tokens_tema(texto)
        pres = self.presencia(tema)
        imp = int(pres["impressions"].sum()) if len(pres) else 0
        if ex is not None:
            return "query presente", imp, ex
        if imp == 0:
            return "sin nada del tema", 0, None
        if imp >= umbral_fuerte:
            return "tema fuerte, query no", imp, None
        return "tema debil", imp, None
