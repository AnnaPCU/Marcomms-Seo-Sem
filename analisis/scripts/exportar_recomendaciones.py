# -*- coding: utf-8 -*-
"""
exportar_recomendaciones.py — junta en un solo JSON todas las recomendaciones que producen los informes,
con una clave estable por recomendación para que el tablero (Marcomms SEO-SEM) no las duplique mes a mes.

Fuentes (se ejecutan los generadores con la escritura de archivos anulada, así se obtiene el texto ya renderizado):
  - generar_plan_unificado.py      → pain point / mejora por unidad (SEM)
  - generar_propuestas_anuncios.py → propuestas de copy por grupo de anuncios (SEM)
  - generar_seo.py                 → recomendaciones por propiedad de Search Console (SEO)

Salida: informe/recomendaciones.json  (lista de dicts; ver CAMPOS abajo)
Uso:    python exportar_recomendaciones.py [AAAA-MM]   (mes de alta; por defecto el mes actual)
"""
import builtins, contextlib, html, io, json, os, re, sys, unicodedata
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
INF = os.path.join(ROOT, "informe")
MES = sys.argv[1] if len(sys.argv) > 1 else pd.Timestamp.today().strftime("%Y-%m")

MARCA = {"Control Union": "CU", "ISO 27001 · campañas «PCU»": "PCU", "ISO 27001 (PCU)": "PCU", "Peterson Solutions": "PS"}
SITIO_DE = {"España": "espana.controlunion.com", "Portugal": "portugal.controlunion.com", "Norteamérica": "northamerica.controlunion.com",
            "Argentina": "argentina.controlunion.com", "Perú": "peru.controlunion.com", "México": "mexico.controlunion.com",
            "Brasil": "brasil.controlunion.com", "Chile": "chile.controlunion.com",
            "Américas": "americas.peterson-solutions.com", "Iberia": "iberia.peterson-solutions.com"}
RENOMBRES = {"PCU Argentina": "PCU Tech"}  # prefijos que cambiaron en la cuenta después de escribir los informes
PREFIJO_UNIDAD = {("CU", "España"): "CU España", ("CU", "Portugal"): "CU Portugal", ("CU", "Canadá"): "CU Canada",
                  ("CU", "CUC USA"): "CU United States", ("CU", "Argentina"): "CU Argentina", ("PS", "Argentina"): "PS Argentina"}


def slug(s, n=60):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:n]


def strip(s):
    return html.unescape(re.sub(r"<[^>]+>", "", str(s))).strip()


def primera_oracion(texto, n=90):
    """Primera oración del texto (un punto seguido de espacio y mayúscula), recortada a n caracteres en un espacio."""
    o = re.split(r"(?<=[.!?:])\s+(?=[A-ZÁÉÍÓÚÑ«/])", texto, maxsplit=1)[0].rstrip(".:")
    if len(o) > n:
        o = o[:n].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return o


def ejecutar(nombre, inyectar):
    """Ejecuta un generador con open() en modo escritura anulado y devuelve su espacio de nombres."""
    ruta = os.path.join(SCRIPTS, nombre)
    src = open(ruta, encoding="utf-8").read()
    for fn in inyectar:
        src = src.replace(f"def {fn}(", f"def _{fn}_original(")
    real_open = builtins.open

    def fake_open(f, mode="r", *a, **k):
        if "w" in mode or "a" in mode:
            return io.StringIO()
        return real_open(f, mode, *a, **k)

    ctx = {"__name__": "exportar", "__file__": ruta, "open": fake_open, **inyectar}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src, nombre, "exec"), ctx)
    return ctx


# ------------------------------------------------------------------ campañas reales, para asignar cada mejora a una
snaps = sorted(d for d in os.listdir(os.path.join(ROOT, "datos", "ads", "api")) if d.startswith("estructura_"))
CAMPANAS = []
if snaps:
    df = pd.read_csv(os.path.join(ROOT, "datos", "ads", "api", snaps[-1], "campanas.csv"), encoding="utf-8-sig")
    CAMPANAS = df["campaign.name"].tolist()
    KW = pd.read_csv(os.path.join(ROOT, "datos", "ads", "api", snaps[-1], "keywords.csv"), encoding="utf-8-sig")
    KW = KW[(KW["ad_group_criterion.negative"] != True) & (KW["ad_group_criterion.status"] == "ENABLED")]

# ------------------------------------------------------------------ búsquedas orgánicas del tema de una campaña o grupo
# Mismo método que analisis_anuncios.py: los 2 temas más repetidos en las keywords -> queries de Search Console del
# sitio que corresponde, hechas desde el país de la campaña, en todo el histórico guardado.
sys.path.insert(0, SCRIPTS)
from lib_analisis import cargar_hist, agregar, tokens_tema  # noqa: E402
ORG = {}
for _m in ("cu", "ps"):
    _q = cargar_hist(_m, "queries_agg")
    for _p in _q["property"].unique():
        ORG[_p] = _q[_q["property"] == _p]
PROP = {"CU España": ("España", "esp"), "CU Portugal": ("Portugal", "prt"), "CU Canada": ("Norteamérica", "can"),
        "CU United States": ("Norteamérica", "usa"), "CU Argentina": ("Argentina", "arg"), "PCU España": ("España", "esp"),
        "PCU Argentina": ("Argentina", "arg"), "PCU Tech": ("Argentina", "arg"), "PS Argentina": ("Américas", "arg")}


def organico_de(campana, grupo=None, texto=""):
    if not campana:
        return []
    nombre = re.sub(r"^PCU\s*-\s*", "PCU ", campana)
    pref = next((k for k in PROP if nombre.startswith(k)), None)
    if not pref or PROP[pref][0] not in ORG:
        return []
    prop, pais = PROP[pref]
    k = KW[KW["campaign.name"] == campana]
    if grupo is not None and (k["ad_group.name"] == grupo).any():
        k = k[k["ad_group.name"] == grupo]
    cuenta = {}
    for t in k["ad_group_criterion.keyword.text"].astype(str):
        for tk in tokens_tema(t):
            cuenta[tk] = cuenta.get(tk, 0) + 1
    # si el texto de la mejora nombra alguno de los temas, esos van primero
    en_texto = set(tokens_tema(texto))
    tema = sorted(cuenta, key=lambda tk: (tk not in en_texto, -cuenta[tk]))[:2]
    # el segundo tema solo cuenta si pesa al menos la mitad que el primero (evita «certificadora» junto a «27001»)
    if len(tema) == 2 and cuenta[tema[1]] < cuenta[tema[0]] / 2:
        tema = tema[:1]
    if not tema:
        return []
    o = agregar(ORG[prop][ORG[prop]["country"] == pais], ["query"])
    # piso de 10 impresiones: por debajo son coincidencias sueltas de una palabra (p. ej. «supply chain» en Canadá)
    o = o[(o["impressions"] >= 10) & o["query"].map(lambda q: bool(set(tokens_tema(q)) & set(tema)))].sort_values("impressions", ascending=False)
    return [{"query": x["query"], "impr": int(x["impressions"]), "pos": round(float(x["position"]), 1)} for _, x in o.head(8).iterrows()]


PAIS_NOMBRE = {"esp": "España", "prt": "Portugal", "can": "Canadá", "usa": "CUC USA", "arg": "Argentina"}


def organico_desde(campana):
    """País desde el que se miden las búsquedas orgánicas de la campaña (el de la campaña, no el de la unidad)."""
    nombre = re.sub(r"^PCU\s*-\s*", "PCU ", campana or "")
    pref = next((k for k in PROP if nombre.startswith(k)), None)
    return PAIS_NOMBRE.get(PROP[pref][1]) if pref else None


def campana_para(marca, unidad, texto):
    """Busca la campaña de la unidad cuyo nombre corto aparece en el texto del pain point."""
    if marca == "PCU":
        cands = [c for c in CAMPANAS if c.startswith("PCU")]
    else:
        pref = PREFIJO_UNIDAD.get((marca, unidad))
        cands = [c for c in CAMPANAS if pref and c.startswith(pref)]
    t = slug(texto, 400)
    mejores = []
    for c in cands:
        corto = re.sub(r"\s*-\s*search\s*$", "", c, flags=re.I).split(" - ", 1)[-1]
        toks = [x for x in re.split(r"[^a-z0-9]+", slug(corto, 100)) if len(x) >= 3 and x not in ("suse", "suso", "cesu", "organic", "tech")]
        if toks and any(x in t for x in toks):
            mejores.append((sum(x in t for x in toks), c))
    return max(mejores)[1] if mejores else None


# ------------------------------------------------------------------ tipo de mejora (filtro del tablero)
# Se clasifica por lo que la mejora pide hacer (no por el problema): una tarjeta puede tener varios tipos.
ACCIONES = [
    ("anuncio", r"\banuncio|\bt[ií]tulo|descripci"),
    ("keywords", r"exacta|\bfrase\b|amplia|keyword|sumar \[|\[[a-z0-9]"),
    ("negativas", r"negativ"),
    ("estructura", r"^campa[nñ]a|\bgrupo|campa[nñ]a (propia|de )|renombrar|separar"),
    ("pausa", r"pausar|\bcpc\b|\btope\b|presupuesto"),
    ("landing", r"landing|p[aá]gina"),
    ("revisar", r"verificar por qu|revisar|definir"),
]


def acciones_de(texto, base=()):
    t = texto.lower()
    return [a for a, rx in ACCIONES if a in base or re.search(rx, t)]


salida = []

# ------------------------------------------------------------------ 1. plan unificado (pain point → mejora)
filas = []
unidades = []


def row(pain, pain_txt, fix, fix_txt, estado="Pendiente"):
    filas.append(dict(pain=strip(pain), pain_txt=strip(pain_txt), fix=strip(fix), fix_txt=strip(fix_txt), estado=estado, unidad=None))
    return ""


def unit(brand, titulo, sub, nums, lead, rows):
    for f in filas:
        if f["unidad"] is None:
            f["unidad"] = (brand, titulo)
    return ""


ejecutar("generar_plan_unificado.py", {"row": row, "unit": unit})
ESTADO = {"Pendiente": ("propuesta", "media"), "Nuevo": ("propuesta", "alta"), "Decisión": ("propuesta", "alta"), "Hecho": ("hecha", "media")}
for f in filas:
    marca = MARCA[f["unidad"][0]]
    unidad = f["unidad"][1]
    estado, prioridad = ESTADO[f["estado"]]
    camp = campana_para(marca, unidad, f["pain"] + " " + f["fix"])
    salida.append(dict(
        # clave estable: no depende del nombre de la campaña en Google Ads (cambia seguido); ver docs/DECISIONES.md del tablero
        clave=f"{marca}:SEM:plan:{slug(unidad)}:{slug(f['pain'])}",
        marca=marca, tipo="SEM", campana=camp, grupo=None, sitio=None, pagina=None,
        titulo=f"{f['fix']} — {f['pain']}", detalle=f"{f['fix_txt']}\n\nPain point: {f['pain_txt']}",
        evidencia={"ficha": "plan", "unidad": unidad, "estado_en_plan": f["estado"], "pain": f["pain"], "pain_txt": f["pain_txt"],
                   "mejora": f["fix"], "mejora_txt": f["fix_txt"],
                   "organico": organico_de(camp, texto=f["pain"] + " " + f["fix"]), "organico_hasta": "14 sep 2026", "organico_desde": organico_desde(camp),
                   "acciones": acciones_de(f["fix"] + " " + f["fix_txt"])}, prioridad=prioridad, estado=estado,
        mes_alta=MES, origen="Plan de mejoras unificado",
    ))

# ------------------------------------------------------------------ 2. propuestas de anuncios (copy por grupo)
FUERZA = {"POOR": "pobre", "AVERAGE": "media", "GOOD": "buena", "EXCELLENT": "excelente"}
ctx = ejecutar("generar_propuestas_anuncios.py", {})
n_anuncios = len(ctx["P"])
for p in ctx["P"]:
    marca = MARCA[p["marca"]]
    d = p["datos"] or {}
    detalle = (p["diagnostico"] + "\n\nTítulos propuestos: " + " | ".join(p["titulos"]) +
               "\n\nDescripciones propuestas: " + " | ".join(p["descripciones"]) +
               (("\n\nQuitar: " + " · ".join(p["quitar"])) if p["quitar"] else "") + (("\n\n" + p["nota"]) if p["nota"] else ""))
    pref = p["camp"].split(" - ")[0]
    alias = RENOMBRES.get(pref, pref) + p["camp"][len(pref):]  # p. ej. "PCU Argentina - ISO 27001" -> "PCU Tech - ISO 27001"
    camp = next((c for c in CAMPANAS if c.startswith(p["camp"]) or c.startswith(alias)), p["camp"])
    salida.append(dict(
        clave=f"{marca}:SEM:anuncio:{slug(p['camp'])}:{slug(p['grupo'])}",  # p["camp"] es el nombre fijo del generador
        marca=marca, tipo="SEM", campana=camp, grupo=p["grupo"], sitio=None, pagina=None,
        titulo=(f"Grupo nuevo con anuncio propio: {p['grupo']}" if p["cambio"] == "Grupo nuevo" else f"{p['cambio']} el anuncio de {p['grupo']}"), detalle=detalle,
        evidencia={
            "ficha": "anuncio", "unidad": p["unidad"], "cambio": p["cambio"], "gasto_ars": round(d.get("coste", 0) or 0),
            "fuerza": [FUERZA.get(x, x.lower()) for x in d.get("fuerza", [])], "url": d.get("url", ""),
            "titulos_hoy": d.get("titulos", []),
            "terminos": [{"termino": x["termino"], "relacion": x["relacion_anuncio"], "coste": round(float(x["coste"])), "clics": int(x.get("clics", 0) or 0)}
                         for x in d.get("terminos", [])[:8]],
            # los grupos sin gasto (o nuevos) no pasan por analisis_anuncios.py: se calcula acá con las keywords
            "organico": ([{"query": x["query"], "impr": int(x["impr"]), "pos": round(float(x["pos"]), 1)} for x in d.get("organico", [])[:8]]
                         or organico_de(camp, p["grupo"], p["grupo"])),
            "diagnostico": p["diagnostico"], "titulos_propuestos": p["titulos"], "descripciones_propuestas": p["descripciones"],
            "quitar": p["quitar"], "nota": p["nota"],
            "ventanas": "1 ago – 24 sep 2026", "organico_hasta": "14 sep 2026", "organico_desde": organico_desde(camp),
            "acciones": acciones_de(" ".join(filter(None, [p["nota"], " ".join(p["quitar"])])),
                                    base=("anuncio",) + (("estructura",) if p["cambio"] == "Grupo nuevo" else ())),
        },
        prioridad="alta" if (d.get("coste") or 0) > 40000 else "media", estado="propuesta", mes_alta=MES, origen="Propuestas de anuncios",
    ))

# ------------------------------------------------------------------ 3. SEO por propiedad
ctx = ejecutar("generar_seo.py", {})
for prop, items in ctx["REC"].items():
    marca = "PS" if prop in ("Américas", "Iberia") else "CU"
    for i, (tag, texto) in enumerate(items):
        salida.append(dict(
            clave=f"{marca}:SEO:{slug(SITIO_DE[prop])}:{slug(tag)}",
            marca=marca, tipo="SEO", campana=None, grupo=None, sitio=SITIO_DE[prop], pagina=None,
            titulo=f"{tag}: {primera_oracion(texto)}", detalle=texto,
            evidencia={"propiedad": prop}, prioridad="alta" if i == 0 else "media", estado="propuesta", mes_alta=MES,
            origen="Recomendaciones SEO para los sitios",
        ))

claves = [s["clave"] for s in salida]
assert len(claves) == len(set(claves)), "claves duplicadas: " + str({c for c in claves if claves.count(c) > 1})
json.dump(salida, open(os.path.join(INF, "recomendaciones.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"-> informe/recomendaciones.json: {len(salida)} recomendaciones "
      f"(SEM plan {len(filas)}, anuncios {n_anuncios}, SEO {sum(len(v) for v in ctx['REC'].values())})")
sin_camp = [s for s in salida if s["tipo"] == "SEM" and not s["campana"]]
print(f"   SEM sin campaña asignada (quedan a nivel unidad): {len(sin_camp)}")
for s in sin_camp:
    print("    -", s["marca"], s["evidencia"].get("unidad"), "|", s["titulo"][:70])
