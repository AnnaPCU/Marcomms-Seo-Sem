# -*- coding: utf-8 -*-
"""
analisis.py — FASE 3. Los seis cruces de CLAUDE.md §6 sobre el histórico nuevo, más
lo que la ventana de 12 meses no permitía:
  · evolución mensual de posiciones de la zona 8-20
  · estacionalidad por norma y por país (donde hay dos años)
  · queries que aparecieron / desaparecieron
  · reparto móvil vs escritorio

Fuentes:
  Ads   datos/ads/ (1 ago – 11 sep 2026)
  GSC   datos/gsc-historico/<marca>/  (hist_*)   y  datos/gsc/ (baseline, idéntico a la API hoy)

Salida:
  informe/datos_informe.json                    números que usa el informe
  datos/gsc-historico/<marca>/analisis/*.csv    tablas detalladas, por marca
"""
import json, os, re
import pandas as pd
from lib_analisis import *

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)
OUT_JSON = os.path.join(ROOT, "informe", "datos_informe.json")
os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
R = {}                                            # resultados para el informe
A, B = VENTANA_ADS


def out_dir(m):
    d = os.path.join(HIST, m, "analisis")
    os.makedirs(d, exist_ok=True)
    return d


def guardar(m, nombre, df):
    df.to_csv(os.path.join(out_dir(m), nombre + ".csv"), index=False, encoding="utf-8-sig")


# ============================================================ carga
st = cargar_terminos()
kw = cargar_keywords()
H = {}
for m in ("cu", "ps"):
    H[m] = {c: cargar_hist(m, c) for c in
            ("queries", "pages", "query_page", "devices", "daily", "queries_agg", "device_total", "device_date")}
    for c in ("queries", "pages", "daily", "device_date"):
        H[m][c]["mes"] = H[m][c]["date"].str[:7]
props = {"cu": list(H["cu"]["daily"]["property"].unique()), "ps": list(H["ps"]["daily"]["property"].unique())}
marca_de = {p: m for m in props for p in props[m]}


def hist(prop, corte):
    return H[marca_de[prop]][corte][H[marca_de[prop]][corte]["property"] == prop]


# ============================================================ 0. panorama
pan = []
for m in ("cu", "ps"):
    d = H[m]["daily"]
    for p, g in d.groupby("property"):
        ga = g[(g["date"] >= A) & (g["date"] <= B)]
        qa = hist(p, "queries_agg")
        pan.append(dict(marca=m.upper(), propiedad=p, primera=g["date"].min(), ultima=g["date"].max(),
                        dias=len(g), impr_total=int(g["impressions"].sum()), clics_total=int(g["clicks"].sum()),
                        impr_ads=int(ga["impressions"].sum()), clics_ads=int(ga["clicks"].sum()),
                        queries_hist=len(qa), pos_media_q=round((qa["position"] * qa["impressions"]).sum() / qa["impressions"].sum(), 1),
                        con_campana=g["con_campana"].iloc[0]))
pan = pd.DataFrame(pan).sort_values("impr_total", ascending=False)
R["panorama"] = pan.to_dict("records")
print("\n0. PANORAMA\n", pan.to_string(index=False))

# ============================================================ desperdicio (Anexo A de la auditoría de Ads)
ANEXO_A = {
    ("España", "CAEs"): "vivienda particular particulares gratis barato precio cuanto cuesta ce3x ce3 certicalia online sin visita descargar euskadi cantabria aragon unifamiliar cuando te caes db he1 cypetherm emovili repsol iberdrola endesa coche electrico aislamiento",
    ("Américas", "Agricultura regenerativa"): "rizobacter syngenta corteva bayer nutrien yara koppert adecoagro bioceres agrofy inta aapresid conabia inase upl adama sipcam daymsa spraytec nufarm stoller verdesian novonesis dekalb puna bio ovis 21 ruuts caligenia sembra evolucion argenbio|tecnologia agricola|tecnologia para la agricultura|agricultura innovadora|agtech|smart farming|agricultura de precision|nuevas tecnologias|sensores|monitores|fieldview|ndvi|sintropica|agroforesteria|permacultura|polyfarming|huerto|granja|olivar|libros|ernst gotsch",
    ("CU", "*"): "consultant|consultor|consultoria|advisor|asesoramiento",
    ("Américas", "Bioenergia / Biocombustibles"): "biogas|bio gas|biometano|planta de|produccion de|que es|como generar|residuos organicos|dosbio|biodes|fenix|doble l|ceamse|helios",
    ("Américas", "Huella de carbono / GEI"): "bonos de carbono|bono de carbono|mercado de carbono|mercados de carbono|creditos de carbono|credito de carbono|verra|cercarbono|carbono neutral|carbon neutral|carbono neutro|carbon trading|cuotas de carbono|iso 14001|persefoni|carboncloud|carbon cloud|puma|ndc|renami",
    ("Norteamérica", "Forestry"): "registered professional forester|rpf|forester license|forestry certificate online|courses|enform|falling ticket|tree felling|bc forest safety|accreditation board|how to become|job|training",
    ("España", "Textile"): "oeko tex|oeko-tex|oeko|organic cotton standard",
    ("Norteamérica", "Canada Gap"): "supply chain management|indocert|cargill|organic certification|forms|corrective action report",
    ("Norteamérica", "USDA NOP"): "organic chicken|chicken certification|organic land certification|omri",
    ("Américas", "Huella de agua"): "tratamiento|efluentes|aguas residuales|calculadora|aquae|planta de tratamiento",
    ("España", "IFS"): "servsafe|certifood|manipulacion de alimentos|food handler|food handling|curso|cursos|salsa accreditation",
    ("España", "Forestal"): "rainforest alliance|medio ambiente",          # fsc quitado: negativo corregido (§7)
    ("Américas", "ESG / Reportes"): "gri \\d+|que es|que significa|que son|eqsc|verdantix",
    ("Portugal", "Textile"): "wordly|database",
    ("Portugal", "Forestal"): "ecocert",                                   # fsc quitado: negativo corregido (§7)
    ("Argentina", "ISO 27001"): "nist",
}


def _rx(spec):
    if "|" in spec:
        partes = [p.strip() for p in spec.split("|") if p.strip()]
    else:
        partes = spec.split()
    return re.compile(r"(?<![a-z0-9])(" + "|".join(re.escape(p) if "\\d" not in p else p for p in partes) + r")(?![a-z0-9])")


RX_A = {k: _rx(v) for k, v in ANEXO_A.items()}


def es_desperdicio(row):
    t = row["termino_n"]
    for (prop, camp), rx in RX_A.items():
        if prop == "CU":
            if row["marca"] == "CU" and rx.search(t):
                return True
        elif row["propiedad"] == prop and row["camp_corta"] == camp and rx.search(t):
            return True
    return False


st["desperdicio"] = st.apply(es_desperdicio, axis=1)
R["ads"] = dict(terminos=len(st), coste_visible=round(st["coste"].sum()), clics_visibles=int(st["clics"].sum()),
                terminos_con_clic=int((st["clics"] > 0).sum()),
                desperdicio_coste=round(st.loc[st["desperdicio"], "coste"].sum()),
                desperdicio_terminos=int(st["desperdicio"].sum()))
print("\nAds:", R["ads"])

# ============================================================ índices GSC por propiedad (ventana Ads, sin date)
IDX_ADS, IDX_HIST = {}, {}
# Cada campaña compra en UN país: el cruce se hace contra las queries de ese país en la
# propiedad (esp, prt, can, usa, arg). Promediar todos los países arrastra la posición con
# filas extranjeras de pocas impresiones: así salieron las posiciones 12-16 del informe anterior.
PAISES = {"España": ["esp"], "Portugal": ["prt"], "Norteamérica": ["can", "usa"], "Argentina": ["arg"], "Américas": ["arg"]}
for m in ("cu", "ps"):
    bq = cargar_base(m, "ads", "queries")
    for p in props[m]:
        IDX_HIST[p] = IndiceTema(agregar(hist(p, "queries_agg"), ["query"]))
        for pais in PAISES.get(p, []):
            IDX_ADS[(p, pais)] = IndiceTema(agregar(bq[(bq["property"] == p) & (bq["country"] == pais)], ["query"]))


def idx_ads(row):
    return IDX_ADS[(row["propiedad"], row["pais"])]


# ============================================================ 1-3. canibalización, zona 8-20, huecos
rel = st[(st["clics"] > 0) & (~st["desperdicio"]) & (st["propiedad"] != "?")].copy()
filas = []
for _, r in rel.iterrows():
    ix = idx_ads(r)
    grupo, imp_tema, ex = ix.clasificar(r["termino"])
    filas.append(dict(grupo=grupo, impr_tema=imp_tema,
                      pos_org=None if ex is None else float(ex["position"]),
                      impr_org=None if ex is None else int(ex["impressions"]),
                      clics_org=None if ex is None else int(ex["clicks"])))
rel = pd.concat([rel.reset_index(drop=True), pd.DataFrame(filas)], axis=1)
# bandas sobre la posición redondeada (7,4 -> 7 -> "4-7"; 7,6 -> 8 -> "8-20"): regla explícita y reproducible
rel["pos_red"] = rel["pos_org"].map(lambda p: None if pd.isna(p) else int(p + 0.5))
rel["banda"] = pd.cut(rel["pos_red"], [0, 3, 7, 20, 1000], labels=["1-3", "4-7", "8-20", "21+"])
grupos = rel.groupby("grupo").agg(terminos=("termino", "count"), coste=("coste", "sum")).round(0)
grupos["pct"] = (grupos["coste"] / rel["coste"].sum() * 100).round(1)
print("\n1-3. TÉRMINOS RELEVANTES CON CLIC:", len(rel), "coste", round(rel["coste"].sum()))
print(grupos.to_string())
R["cobertura"] = dict(terminos=len(rel), coste=round(rel["coste"].sum()),
                      grupos={g: dict(terminos=int(x["terminos"]), coste=int(x["coste"]), pct=float(x["pct"]))
                              for g, x in grupos.iterrows()})
canib = rel[rel["banda"] == "1-3"]
canib7 = rel[rel["banda"].isin(["1-3", "4-7"])]
zona = rel[rel["banda"] == "8-20"].sort_values("coste", ascending=False)
R["canibalizacion"] = dict(coste_1_3=round(canib["coste"].sum()), terminos_1_3=len(canib),
                           coste_1_7=round(canib7["coste"].sum()), terminos_1_7=len(canib7),
                           pct=round(canib["coste"].sum() / rel["coste"].sum() * 100, 1),
                           top=canib.sort_values("coste", ascending=False)[["termino", "campana", "coste", "pos_org", "clics_org"]].head(8).to_dict("records"))
R["zona_todos"] = rel[["termino", "propiedad", "pais", "coste", "impr_org", "pos_org"]].to_dict("records")
R["zona_8_20"] = dict(coste=round(zona["coste"].sum()), terminos=len(zona),
                      top=zona[["termino", "propiedad", "pais", "camp_corta", "coste", "impr_org", "pos_org"]].head(12).to_dict("records"))
print("\nCanibalización 1-3:", R["canibalizacion"]["coste_1_3"], "| 1-7:", R["canibalizacion"]["coste_1_7"])
print("Zona 8-20:", R["zona_8_20"]["coste"], "en", len(zona), "términos")
print(zona[["termino", "propiedad", "pais", "coste", "impr_org", "pos_org"]].head(12).to_string(index=False))
for m in ("cu", "ps"):
    guardar(m, "cruce_terminos_relevantes", rel[rel["marca"] == m.upper()].drop(columns=["tema"]))

# huecos por campaña
huecos = rel[rel["grupo"] == "sin nada del tema"].groupby(["marca", "propiedad", "pais", "camp_corta"]).agg(
    coste=("coste", "sum"), terminos=("termino", "count")).round(0).sort_values("coste", ascending=False).reset_index()
R["huecos_por_campana"] = huecos.head(12).to_dict("records")
print("\nHuecos por campaña:\n", huecos.head(12).to_string(index=False))

# ============================================================ evolución mensual de la zona 8-20 (España)
CINCO = ["global recycled standard", "recyclass", "smeta", "iscc", "pefc"]
hq = hist("España", "queries")
hq = hq[hq["country"] == "esp"]                      # la campaña compra en España
ev = []
for t in CINCO:
    g = hq[hq["query"] == t]
    gm = agregar(g, ["mes"])
    for _, r in gm.iterrows():
        ev.append(dict(termino=t, mes=r["mes"], impr=int(r["impressions"]), clics=int(r["clicks"]), pos=r["position"]))
ev = pd.DataFrame(ev)
piv = ev.pivot(index="termino", columns="mes", values="pos").reindex(CINCO)
print("\nEvolución mensual posición · España · cinco términos zona 8-20\n", piv.round(1).to_string())
R["evolucion_cinco"] = {t: {m: (None if pd.isna(v) else round(float(v), 1)) for m, v in row.items()} for t, row in piv.iterrows()}
R["evolucion_cinco_impr"] = ev.pivot(index="termino", columns="mes", values="impr").reindex(CINCO).fillna(0).astype(int).to_dict("index")
guardar("cu", "evolucion_zona_8_20_espana", ev)
# los cinco de la zona 8-20 según ESTA medición (posición exacta de la query en la ventana de Ads), con su evolución
top5 = zona.drop_duplicates("termino").head(5)
ev2 = {}
for _, r in top5.iterrows():
    g = hist(r["propiedad"], "queries")
    g = g[g["country"] == r["pais"]]
    gm = agregar(g[g["query"] == r["termino"]], ["mes"]).set_index("mes")
    ev2[f"{r['termino']} · {r['pais']}"] = {m: round(float(gm.loc[m, "position"]), 1) if m in gm.index else None
                                                 for m in sorted(hq["mes"].unique())}
R["evolucion_zona_top5"] = ev2
print("\nEvolución mensual · top 5 de la zona 8-20 de esta medición\n", pd.DataFrame(ev2).T.to_string())
# referencia: qué decía el baseline 12m sobre los cinco del informe anterior (exacto y por tema)
b12raw = cargar_base("cu", "12m", "queries")
b12raw = b12raw[b12raw["property"] == "España"]
ref = {}
for t in CINCO:
    y = b12raw[b12raw["query"] == t]
    ye = y[y["country"] == "esp"]
    ref[t] = dict(filas_pais=len(y), impr_total=int(y["impressions"].sum()),
                  media_simple=round(float(y["position"].mean()), 1) if len(y) else None,
                  ponderada=round(float((y["position"] * y["impressions"]).sum() / y["impressions"].sum()), 1) if len(y) else None,
                  impr_esp=int(ye["impressions"].sum()), pos_esp=round(float(ye["position"].iloc[0]), 1) if len(ye) else None)
R["cinco_referencia_12m"] = ref
print("\nReferencia baseline 12m España, cinco términos del informe anterior:", ref)
# todos los términos de la zona 8-20 de España: primer mes completo vs último mes completo
zona_es = zona[zona["propiedad"] == "España"]["termino"].tolist()
comp = []
for t in zona_es:
    g = agregar(hq[hq["query"] == t], ["mes"]).set_index("mes")
    if "2026-04" in g.index and "2026-08" in g.index:
        comp.append(dict(termino=t, pos_abr=g.loc["2026-04", "position"], pos_ago=g.loc["2026-08", "position"],
                         impr_abr=int(g.loc["2026-04", "impressions"]), impr_ago=int(g.loc["2026-08", "impressions"])))
comp = pd.DataFrame(comp)
if len(comp):
    comp["delta"] = (comp["pos_ago"] - comp["pos_abr"]).round(1)
    print("\nZona 8-20 España: abril vs agosto 2026\n", comp.to_string(index=False))
    R["zona_abr_ago"] = comp.to_dict("records")

# ============================================================ 4. demanda no comprada
comprado = {}
for p in set(props["cu"]) | set(props["ps"]):
    temas = set()
    for df, col in ((kw, "tema"), (st, "tema")):
        for t in df.loc[df["propiedad"] == p, col]:
            if t:
                temas.add(t)
    comprado[p] = temas


def esta_comprada(tema, temas):
    if not tema:
        return True
    s = set(tema)
    for t in temas:
        ts = set(t)
        if ts <= s or s <= ts:
            return True
    return False


nc_res, nc_tablas = {}, []
for m in ("cu", "ps"):
    qa = agregar(H[m]["queries_agg"], ["property", "query"])
    qa = qa[qa["impressions"] >= 40].copy()
    # se excluyen búsquedas de marca propia y navegacionales: no son demanda de servicio
    marca_rx = r"control ?union|peterson|\blogin\b|\bcu\b|\bpcu\b"
    qa = qa[~qa["query"].map(lambda s: bool(re.search(marca_rx, normalizar(s))))]
    qa["tema"] = qa["query"].map(tokens_tema)
    qa["norma"] = qa["query"].map(etiquetar_norma)
    qa["comprada"] = [esta_comprada(t, comprado.get(p, set())) for t, p in zip(qa["tema"], qa["property"])]
    nc = qa[~qa["comprada"]].sort_values(["property", "impressions"], ascending=[True, False])
    guardar(m, "demanda_no_comprada", nc.drop(columns=["tema"]))
    for p, g in nc.groupby("property"):
        con = "si" if H[m]["daily"].loc[H[m]["daily"]["property"] == p, "con_campana"].iloc[0] == "si" else "no"
        nc_res[p] = dict(queries=len(g), impresiones=int(g["impressions"].sum()), clics=int(g["clicks"].sum()),
                         con_campana=con,
                         top=g[["query", "impressions", "clicks", "position", "norma"]].head(10).to_dict("records"))
        tot = qa[qa["property"] == p]
        nc_res[p]["queries_40"] = len(tot)
        nc_res[p]["pct_no_comprada"] = round(len(g) / len(tot) * 100, 1) if len(tot) else None
R["no_comprada"] = nc_res
print("\n4. DEMANDA NO COMPRADA (queries 40+ impr. en todo el histórico, sin keyword ni término por tema)")
for p, v in nc_res.items():
    print(f"  {p:<13} {v['queries']:>5} de {v['queries_40']:>5} queries ({v['pct_no_comprada']}%)  {v['impresiones']:>8,} impr   top: "
          + ", ".join(f"{t['query']} ({t['impressions']:,})" for t in v["top"][:4]))

# ============================================================ 5. landing desalineada (solo keywords con URL final en el export)
land = []
kwu = kw[kw["url_final"].notna() & (kw["url_final"] != "")]
for _, r in kwu.iterrows():
    qp = hist(r["propiedad"], "query_page")
    ex = qp[qp["query"] == r["keyword_n"]]
    if len(ex) == 0:
        tema = r["tema"]
        ex = qp[qp["query"].map(lambda q: set(tema) <= set(tokens_tema(q)) if tema else False)]
    if len(ex) == 0:
        continue
    top = agregar(ex, ["page"]).sort_values("impressions", ascending=False).iloc[0]
    land.append(dict(keyword=r["keyword"], campana=r["camp_corta"], propiedad=r["propiedad"], url_final=r["url_final"],
                     pagina_organica=top["page"], impr=int(top["impressions"]), pos=top["position"],
                     coincide=top["page"].rstrip("/") == r["url_final"].rstrip("/")))
land = pd.DataFrame(land).drop_duplicates(["keyword", "campana"])
R["landing"] = dict(keywords_con_url=int(len(kwu)), evaluadas=len(land), coinciden=int(land["coincide"].sum()) if len(land) else 0,
                    detalle=land.to_dict("records"))
print("\n5. LANDING: keywords con URL final en el export:", len(kwu), "| evaluadas:", len(land), "| coinciden:", R["landing"]["coinciden"])
if len(land):
    print(land[["keyword", "propiedad", "url_final", "pagina_organica", "impr", "pos", "coincide"]].to_string(index=False))
guardar("cu", "landing_desalineada", land)

# ============================================================ 6. validación de negativos
neg_rows = []
for (prop, camp), spec in ANEXO_A.items():
    partes = [p.strip() for p in (spec.split("|") if "|" in spec else spec.split())]
    objetivo = props["cu"] if prop == "CU" else [prop]
    for p in objetivo:
        ix = IDX_HIST[p]
        for neg in partes:
            if "\\d" in neg:
                continue
            tema = tokens_tema(neg)
            if not tema:
                continue
            pres = ix.presencia(tema)
            if len(pres):
                neg_rows.append(dict(ambito=f"{prop} · {camp}", propiedad=p, negativo=neg, queries=len(pres),
                                     impresiones=int(pres["impressions"].sum()), clics=int(pres["clicks"].sum()),
                                     pos=round((pres["position"] * pres["impressions"]).sum() / pres["impressions"].sum(), 1),
                                     ejemplo=pres.sort_values("impressions", ascending=False)["query"].iloc[0]))
neg = pd.DataFrame(neg_rows).sort_values("impresiones", ascending=False)
guardar("cu", "validacion_negativos", neg[neg["propiedad"].isin(props["cu"])])
guardar("ps", "validacion_negativos", neg[neg["propiedad"].isin(props["ps"])])
R["negativos"] = dict(evaluados=sum(len((s.split("|") if "|" in s else s.split())) for s in ANEXO_A.values()),
                      con_presencia=len(neg), relevantes=neg[neg["impresiones"] >= 100].to_dict("records"))
print("\n6. NEGATIVOS CON PRESENCIA ORGÁNICA (100+ impr.)\n", neg[neg["impresiones"] >= 100].to_string(index=False))

# ============================================================ 7. re-verificación de CLAUDE.md §7 sobre el histórico completo
def presencia_norma(p, rx, corte="queries_agg"):
    q = hist(p, corte)
    g = q[q["query"].map(lambda s: bool(re.search(rx, normalizar(s))))]
    return dict(queries=int(g["query"].nunique()), impresiones=int(g["impressions"].sum()), clics=int(g["clicks"].sum()),
                pos=round((g["position"] * g["impressions"]).sum() / g["impressions"].sum(), 1) if len(g) else None)


def por_mes_norma(p, rx):
    q = hist(p, "queries")
    g = q[q["query"].map(lambda s: bool(re.search(rx, normalizar(s))))]
    return {m: int(v) for m, v in g.groupby("mes")["impressions"].sum().items()}


S7 = {}
S7["fsc_espana"] = presencia_norma("España", r"\bfsc\b")
S7["fsc_portugal"] = presencia_norma("Portugal", r"\bfsc\b")
S7["oeko_cu"] = {p: presencia_norma(p, r"oeko|okotex|oko tex") for p in props["cu"]}
S7["iso22000_es"] = presencia_norma("España", r"22000")
S7["fssc_es"] = presencia_norma("España", r"\bfssc\b")
S7["brcgs_es"] = presencia_norma("España", r"\bbrc")
S7["gmp_es"] = presencia_norma("España", r"\bgmp")
S7["gmp_pt"] = presencia_norma("Portugal", r"\bgmp")
S7["ifs_es"] = presencia_norma("España", r"\bifs\b")
S7["iso45001_es"] = presencia_norma("España", r"45001")
S7["fsc_na"] = presencia_norma("Norteamérica", r"\bfsc\b|forest")
q = hist("Norteamérica", "queries_agg")
S7["fsc_na_can"] = presencia_norma("Norteamérica", r"\bfsc\b|forest")
gna = q[q["query"].map(lambda s: bool(re.search(r"\bfsc\b|forest", normalizar(s))))]
S7["fsc_na_por_pais"] = gna.groupby("country")["impressions"].sum().sort_values(ascending=False).head(5).to_dict()
S7["temo_na"] = presencia_norma("Norteamérica", r"\btemo\b")
S7["smeta_ar"] = presencia_norma("Argentina", r"\bsmeta\b")
S7["visec_ar"] = presencia_norma("Argentina", r"visec")
S7["queries_cu_total"] = int(sum(hist(p, "queries_agg")["query"].nunique() for p in props["cu"]))
S7["mes_fsc_es"] = por_mes_norma("España", r"\bfsc\b")
S7["mes_gmp_es"] = por_mes_norma("España", r"\bgmp")
S7["mes_iso45001_es"] = por_mes_norma("España", r"45001")
R["s7"] = S7
print("\n7. RE-VERIFICACIÓN §7 (histórico completo, sin date):")
for k, v in S7.items():
    print(f"  {k}: {v}")

# ============================================================ 8. estacionalidad por norma y país
est = {}
for m in ("cu", "ps"):
    q = H[m]["queries"].copy()
    q["norma"] = q["query"].map(etiquetar_norma)
    q = q[q["norma"].notna()]
    tab = q.groupby(["property", "norma", "mes"])["impressions"].sum().reset_index()
    guardar(m, "estacionalidad_norma_mes", tab)
    for p in props[m]:
        t = tab[tab["property"] == p].pivot(index="norma", columns="mes", values="impressions").fillna(0).astype(int)
        t = t.loc[t.sum(axis=1).sort_values(ascending=False).index[:12]]
        est[p] = {n: {mes: int(v) for mes, v in row.items()} for n, row in t.iterrows()}
R["estacionalidad"] = est
# interanual: Argentina y México, jun-jul-ago 2025 vs 2026
yoy = {}
for p in ("Argentina", "México"):
    q = hist(p, "queries").copy()
    q["norma"] = q["query"].map(etiquetar_norma)
    d = hist(p, "daily")
    tot25 = d[d["mes"].isin(["2025-06", "2025-07", "2025-08"])]
    tot26 = d[d["mes"].isin(["2026-06", "2026-07", "2026-08"])]
    yoy[p] = dict(total=dict(impr_2025=int(tot25["impressions"].sum()), impr_2026=int(tot26["impressions"].sum()),
                             clics_2025=int(tot25["clicks"].sum()), clics_2026=int(tot26["clicks"].sum())))
    qn = q[q["norma"].notna()]
    a25 = qn[qn["mes"].isin(["2025-06", "2025-07", "2025-08"])].groupby("norma")["impressions"].sum()
    a26 = qn[qn["mes"].isin(["2026-06", "2026-07", "2026-08"])].groupby("norma")["impressions"].sum()
    t = pd.DataFrame({"impr_2025": a25, "impr_2026": a26}).fillna(0).astype(int)
    t["var_pct"] = [round((b - a) / a * 100) if a else None for a, b in zip(t["impr_2025"], t["impr_2026"])]
    t = t.sort_values("impr_2026", ascending=False)
    yoy[p]["normas"] = t.head(12).reset_index().to_dict("records")
    guardar("cu", f"interanual_{normalizar(p)}", t.reset_index())
    print(f"\n8. INTERANUAL {p} (jun-ago 2025 vs jun-ago 2026): {yoy[p]['total']}\n", t.head(12).to_string())
R["interanual"] = yoy

# ============================================================ 9. queries que aparecieron / desaparecieron
apdes = {}
UMBRAL = 30
for m in ("cu", "ps"):
    filas = []
    for p in props[m]:
        q = hist(p, "queries")
        if p in ("Argentina", "México"):
            t1 = q[q["mes"].isin(["2025-06", "2025-07", "2025-08"])]; t2 = q[q["mes"].isin(["2026-06", "2026-07", "2026-08"])]
            etiq = ("jun-ago 2025", "jun-ago 2026")
        else:
            d0 = q["date"].min()
            t1 = q[q["date"] < "2026-06-01"]; t2 = q[q["date"] >= "2026-06-16"]
            etiq = (f"{d0} a 2026-05-31", "2026-06-16 a 2026-09-13")
        a1 = t1.groupby("query")["impressions"].sum(); a2 = t2.groupby("query")["impressions"].sum()
        ap = a2[(a2 >= UMBRAL) & (~a2.index.isin(a1.index))].sort_values(ascending=False)
        de = a1[(a1 >= UMBRAL) & (~a1.index.isin(a2.index))].sort_values(ascending=False)
        apdes[p] = dict(tramos=etiq, aparecieron=len(ap), desaparecieron=len(de),
                        top_ap=[dict(query=k, impr=int(v), norma=etiquetar_norma(k)) for k, v in ap.head(8).items()],
                        top_de=[dict(query=k, impr=int(v), norma=etiquetar_norma(k)) for k, v in de.head(8).items()])
        for k, v in ap.items():
            filas.append(dict(propiedad=p, tipo="aparecio", query=k, impr=int(v), norma=etiquetar_norma(k)))
        for k, v in de.items():
            filas.append(dict(propiedad=p, tipo="desaparecio", query=k, impr=int(v), norma=etiquetar_norma(k)))
        print(f"\n9. {p}: tramos {etiq} -> aparecieron {len(ap)}, desaparecieron {len(de)} (umbral {UMBRAL} impr.)")
        print("   nuevas:", ", ".join(f"{k} ({int(v)})" for k, v in ap.head(6).items()))
        print("   idas:  ", ", ".join(f"{k} ({int(v)})" for k, v in de.head(6).items()))
    guardar(m, "queries_aparecieron_desaparecieron", pd.DataFrame(filas))
R["aparecieron"] = apdes

# ============================================================ 10. móvil vs escritorio
dev = {}
for m in ("cu", "ps"):
    dt = H[m]["device_total"]
    for p, g in dt.groupby("property"):
        tot_i, tot_c = g["impressions"].sum(), g["clicks"].sum()
        dev[p] = {r["device"]: dict(impr=int(r["impressions"]), clics=int(r["clicks"]),
                                    pct_impr=round(r["impressions"] / tot_i * 100, 1), pct_clics=round(r["clicks"] / tot_c * 100, 1),
                                    ctr=round(r["clicks"] / r["impressions"] * 100, 2) if r["impressions"] else 0,
                                    pos=r["position"]) for _, r in g.iterrows()}
    # por norma (devices = query+device, anonimizado)
    qd = H[m]["devices"].copy()
    qd["norma"] = qd["query"].map(etiquetar_norma)
    tn = qd[qd["norma"].notna()].groupby(["property", "norma", "device"])["impressions"].sum().unstack(fill_value=0)
    tn["pct_mobile"] = (tn.get("MOBILE", 0) / tn.sum(axis=1) * 100).round(1)
    tn = tn.reset_index()
    guardar(m, "movil_por_norma", tn)
    # evolución mensual del reparto
    dd = H[m]["device_date"]
    dm = dd.groupby(["property", "mes", "device"])["impressions"].sum().unstack(fill_value=0)
    dm["pct_mobile"] = (dm.get("MOBILE", 0) / dm.sum(axis=1) * 100).round(1)
    guardar(m, "movil_por_mes", dm.reset_index())
R["dispositivos"] = dev
tot_all = pd.concat([H["cu"]["device_total"], H["ps"]["device_total"]]).groupby("device")[["impressions", "clicks"]].sum()
R["dispositivos_total"] = {d: dict(impr=int(r["impressions"]), clics=int(r["clicks"]),
                                   pct_impr=round(r["impressions"] / tot_all["impressions"].sum() * 100, 1),
                                   pct_clics=round(r["clicks"] / tot_all["clicks"].sum() * 100, 1)) for d, r in tot_all.iterrows()}
print("\n10. DISPOSITIVOS (todo el histórico):", R["dispositivos_total"])
for p, v in dev.items():
    print(f"  {p:<13} " + "  ".join(f"{d}: {x['pct_impr']}% impr / {x['pct_clics']}% clics / CTR {x['ctr']}% / pos {x['pos']}" for d, x in v.items()))
# móvil por norma, agregando marcas por separado
tn_cu = pd.read_csv(os.path.join(out_dir("cu"), "movil_por_norma.csv"))
top_normas = tn_cu.assign(tot=tn_cu[["DESKTOP", "MOBILE", "TABLET"]].sum(axis=1)).groupby("norma").agg(
    tot=("tot", "sum"), MOBILE=("MOBILE", "sum")).sort_values("tot", ascending=False).head(15)
top_normas["pct_mobile"] = (top_normas["MOBILE"] / top_normas["tot"] * 100).round(1)
R["movil_norma_cu"] = top_normas.reset_index().to_dict("records")
print("\nMóvil por norma (CU, top 15 por impresiones):\n", top_normas.to_string())

# ============================================================ 11. archivo, huecos, validación, límites (para el informe)
import glob
cortes_arch, filas_total, mb_total = {}, 0, 0.0
for f in sorted(glob.glob(os.path.join(HIST, "*", "gsc_*_hist_*.csv"))):
    corte = re.sub(r"^gsc_(cu|ps)_hist_", "", os.path.basename(f)).replace(".csv", "")
    nfil = sum(1 for _ in open(f, encoding="utf-8-sig")) - 1
    mb = os.path.getsize(f) / 1e6
    c = cortes_arch.setdefault(corte, dict(filas=0, mb=0.0))
    c["filas"] += nfil; c["mb"] += mb
    filas_total += nfil; mb_total += mb
llamadas = 0
for f in glob.glob(os.path.join(HIST, "*", "log_*.jsonl")):
    llamadas += sum(1 for l in open(f, encoding="utf-8") if '"status": 200' in l)
etiq = {"queries": "queries · query + país + fecha", "pages": "pages · página + fecha", "query_page": "query_page · query + página",
        "devices": "devices · query + dispositivo", "daily": "daily · fecha", "queries_agg": "queries_agg · query + país",
        "device_total": "device_total · dispositivo", "device_date": "device_date · fecha + dispositivo"}
R["archivo"] = dict(filas_total=filas_total, mb_total=round(mb_total, 1), llamadas=llamadas,
                    cortes={etiq.get(k, k): dict(filas=v["filas"], mb=round(v["mb"], 1)) for k, v in cortes_arch.items()})

huecos = {}
for m in ("cu", "ps"):
    for p, g in H[m]["daily"].groupby("property"):
        d = pd.to_datetime(g["date"]).sort_values().reset_index(drop=True)
        dif = d.diff().dt.days
        for i in range(1, len(d)):
            if dif[i] > 1:
                huecos[p] = dict(desde=str((d[i - 1] + pd.Timedelta(days=1)).date()), hasta=str((d[i] - pd.Timedelta(days=1)).date()),
                                 hueco_dias=int(dif[i]) - 1)
R["huecos"] = huecos

val = {"filas_iguales": 0, "detalle": []}
for m in ("cu", "ps"):
    v = pd.read_csv(os.path.join(HIST, m, "validacion_continuidad.csv"))
    for _, r in v.iterrows():
        if str(r["prueba"]).startswith("pages_") and r.get("identico") == True:
            val["filas_iguales"] += int(r["filas_base"])
        if str(r["prueba"]).startswith("queries_") and float(r.get("cobertura_filas", 0)) == 100.0 and int(r.get("hist_excede", 1)) == 0:
            val["filas_iguales"] += int(r["filas_base"])
        val["detalle"].append({k: (None if pd.isna(x) else (x.item() if hasattr(x, "item") else x)) for k, x in r.items()})
R["validacion"] = val

if len(land):
    es = land[land["propiedad"] == "España"]; ar = land[land["propiedad"] == "Argentina"]
    R["landing"]["pos_es"] = float(es["pos"].iloc[0]) if len(es) else None
    R["landing"]["pos_ar"] = float(ar["pos"].iloc[0]) if len(ar) else None

mm = {p: v["MOBILE"]["pct_impr"] for p, v in dev.items() if "MOBILE" in v}
R["movil_max"] = dict(propiedad=max(mm, key=mm.get), pct=mm[max(mm, key=mm.get)])
R["movil_min"] = dict(propiedad=min(mm, key=mm.get), pct=mm[min(mm, key=mm.get)])

d_es = hist("España", "daily")["impressions"].sum()
q_es = hist("España", "queries_agg")["impressions"].sum()
R["limites"] = dict(pct_query_vs_prop_es=round(q_es / d_es * 100, 1))
R["verificacion"] = dict(numeros=0, resultado="pendiente")

# ============================================================ guardar
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=1, default=lambda o: None if pd.isna(o) else str(o))
print("\n-> informe/datos_informe.json")
