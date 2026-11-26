# -*- coding: utf-8 -*-
"""
verificar_informe.py — FASE 4. Recalcula los números principales del informe DIRECTAMENTE
desde los CSV fuente (datos/gsc-historico, datos/gsc, datos/ads), con pandas y sin pasar por
analisis.py ni lib_analisis.py, y los compara con informe/datos_informe.json.

Escribe el resultado en el JSON (clave "verificacion") para que el informe lo declare.
"""
import json, os, re, glob, sys, unicodedata
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST = os.path.join(ROOT, "datos", "gsc-historico")
J = os.path.join(ROOT, "informe", "datos_informe.json")
D = json.load(open(J, encoding="utf-8"))
A, B = "2026-08-01", "2026-09-11"
checks = []


def chk(nombre, esperado, obtenido, tol=0):
    if isinstance(esperado, str) or isinstance(obtenido, str):
        ok = str(esperado) == str(obtenido)
    else:
        ok = (esperado is None and obtenido is None) or (
            esperado is not None and obtenido is not None and abs(float(esperado) - float(obtenido)) <= tol)
    checks.append((nombre, esperado, obtenido, ok))
    print(f"  {'OK ' if ok else 'XX '} {nombre:<58} informe={esperado}  fuente={obtenido}")


def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(c)).lower()
    s = s.replace("-", " ").replace("_", " ").replace("/", " ")
    s = re.sub(r"[\"\[\]'“”]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def h(m, c):
    return pd.read_csv(os.path.join(HIST, m, f"gsc_{m}_hist_{c}.csv"), encoding="utf-8-sig", dtype={"query": str})


print("\n1. Archivo y cobertura")
tot = 0
for f in glob.glob(os.path.join(HIST, "*", "gsc_*_hist_*.csv")):
    tot += sum(1 for _ in open(f, encoding="utf-8-sig")) - 1
chk("filas totales del archivo", D["archivo"]["filas_total"], tot)
dcu, dps = h("cu", "daily"), h("ps", "daily")
d = pd.concat([dcu, dps])
for p in ("España", "Argentina", "México", "Américas"):
    g = d[d["property"] == p]
    pan = next(x for x in D["panorama"] if x["propiedad"] == p)
    chk(f"{p}: primer día", pan["primera"], g["date"].min())
    chk(f"{p}: impresiones totales", pan["impr_total"], int(g["impressions"].sum()))
    chk(f"{p}: clics totales", pan["clics_total"], int(g["clicks"].sum()))
# hueco Argentina
g = pd.to_datetime(dcu[dcu["property"] == "Argentina"]["date"]).sort_values()
gap = int(g.diff().dt.days.max()) - 1
chk("Argentina: días de hueco", D["huecos"]["Argentina"]["hueco_dias"], gap)
g = pd.to_datetime(dcu[dcu["property"] == "México"]["date"]).sort_values()
chk("México: días de hueco", D["huecos"]["México"]["hueco_dias"], int(g.diff().dt.days.max()) - 1)

print("\n2. Continuidad con el baseline (pages, ventana 12m)")
bp = pd.read_csv(os.path.join(ROOT, "datos", "gsc", "gsc_cu_12m_pages.csv"), encoding="utf-8-sig")
hp = h("cu", "pages")
hp = hp[(hp["date"] >= "2025-09-15") & (hp["date"] <= "2026-09-12")].groupby(["property", "page"])[["clicks", "impressions"]].sum().reset_index()
mg = bp.merge(hp, on=["property", "page"], how="outer", indicator=True)
iguales = int(((mg["_merge"] == "both") & (mg["impressions_x"] == mg["impressions_y"]) & (mg["clicks_x"] == mg["clicks_y"])).sum())
chk("pages CU 12m: filas idénticas == filas baseline", len(bp), iguales)

print("\n3. Ads y cruces")
st = pd.read_csv(os.path.join(ROOT, "datos", "ads", "Informe de terminos de busqueda.csv"), skiprows=2, dtype=str)
st = st[st["Campaña"].notna()].copy()
st["coste"] = st["Coste"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)
st["clics"] = st["Clics"].str.replace(".", "", regex=False).astype(int)
chk("Ads: coste visible total", D["ads"]["coste_visible"], round(st["coste"].sum()))
chk("Ads: términos con clic", D["ads"]["terminos_con_clic"], int((st["clics"] > 0).sum()))
# canibalización: recomputada desde el CSV de cruce (los términos y sus posiciones) -- y una muestra a mano
rel = pd.concat([pd.read_csv(os.path.join(HIST, m, "analisis", "cruce_terminos_relevantes.csv"), encoding="utf-8-sig") for m in ("cu", "ps")])
chk("cruce: términos relevantes", D["cobertura"]["terminos"], len(rel))
chk("cruce: coste relevante", D["cobertura"]["coste"], round(rel["coste"].sum()))
pr = rel["pos_org"].map(lambda p: None if pd.isna(p) else int(p + 0.5))     # posición redondeada, misma regla declarada
chk("canibalización 1-3: coste", D["canibalizacion"]["coste_1_3"], round(rel.loc[pr <= 3, "coste"].sum()))
chk("zona 8-20: coste", D["zona_8_20"]["coste"], round(rel.loc[(pr >= 8) & (pr <= 20), "coste"].sum()))
chk("sin nada del tema: coste", D["cobertura"]["grupos"]["sin nada del tema"]["coste"], round(rel.loc[rel["grupo"] == "sin nada del tema", "coste"].sum()))
# muestra a mano: posición orgánica de 'recyclass' en España/esp en la ventana de Ads, desde el baseline
ba = pd.read_csv(os.path.join(ROOT, "datos", "gsc", "gsc_cu_ads_queries.csv"), encoding="utf-8-sig")
for t in ("recyclass", "smeta", "iscc", "pefc"):
    fila = ba[(ba["property"] == "España") & (ba["country"] == "esp") & (ba["query"] == t)]
    en_rel = rel[(rel["termino"] == t) & (rel["propiedad"] == "España")]
    if len(fila) and len(en_rel):
        chk(f"pos. orgánica ESP ventana Ads: {t}", float(en_rel["pos_org"].iloc[0]), float(fila["position"].iloc[0]), 0.01)

print("\n4. Cinco términos del informe anterior (baseline 12m España)")
b12 = pd.read_csv(os.path.join(ROOT, "datos", "gsc", "gsc_cu_12m_queries.csv"), encoding="utf-8-sig")
b12 = b12[b12["property"] == "España"]
for t, r in D["cinco_referencia_12m"].items():
    y = b12[b12["query"] == t]
    ye = y[y["country"] == "esp"]
    chk(f"{t}: media simple (método informe anterior)", r["media_simple"], round(y["position"].mean(), 1), 0.05)
    chk(f"{t}: posición solo ESP", r["pos_esp"], round(float(ye["position"].iloc[0]), 1) if len(ye) else None, 0.05)
    chk(f"{t}: impresiones totales 12m", r["impr_total"], int(y["impressions"].sum()))

print("\n5. Re-verificación §7 (queries_agg, todo el histórico)")
qa = pd.concat([h("cu", "queries_agg"), h("ps", "queries_agg")])
qa["qn"] = qa["query"].map(norm)


def pres(p, rx):
    g = qa[(qa["property"] == p) & qa["qn"].str.contains(rx, regex=True)]
    return int(g["impressions"].sum()), int(g["query"].nunique())


chk("FSC España: impresiones", D["s7"]["fsc_espana"]["impresiones"], pres("España", r"\bfsc\b")[0])
chk("FSC Portugal: impresiones", D["s7"]["fsc_portugal"]["impresiones"], pres("Portugal", r"\bfsc\b")[0])
oeko = sum(pres(p, r"oeko|okotex|oko tex")[0] for p in qa[qa["property"].isin(D["s7"]["oeko_cu"].keys())]["property"].unique())
chk("OEKO-TEX en las 8 de CU: impresiones", sum(v["impresiones"] for v in D["s7"]["oeko_cu"].values()), oeko)
chk("ISO 22000 España: impresiones", D["s7"]["iso22000_es"]["impresiones"], pres("España", r"22000")[0])
chk("BRCGS España: impresiones", D["s7"]["brcgs_es"]["impresiones"], pres("España", r"\bbrc")[0])
chk("GMP+ España: impresiones", D["s7"]["gmp_es"]["impresiones"], pres("España", r"\bgmp")[0])
chk("ISO 45001 España: impresiones", D["s7"]["iso45001_es"]["impresiones"], pres("España", r"45001")[0])
chk("FSC/forest Norteamérica: impresiones", D["s7"]["fsc_na"]["impresiones"], pres("Norteamérica", r"\bfsc\b|forest")[0])
chk("TEMO Norteamérica: impresiones", D["s7"]["temo_na"]["impresiones"], pres("Norteamérica", r"\btemo\b")[0])
cu_q = int(sum(qa[qa["property"] == p]["query"].nunique() for p in D["s7"]["oeko_cu"].keys()))
chk("queries distintas CU (8 propiedades)", D["s7"]["queries_cu_total"], cu_q)

print("\n6. Dispositivos")
dt = pd.concat([h("cu", "device_total"), h("ps", "device_total")])
g = dt.groupby("device")[["impressions", "clicks"]].sum()
chk("móvil: % impresiones", D["dispositivos_total"]["MOBILE"]["pct_impr"], round(g.loc["MOBILE", "impressions"] / g["impressions"].sum() * 100, 1), 0.05)
chk("móvil: % clics", D["dispositivos_total"]["MOBILE"]["pct_clics"], round(g.loc["MOBILE", "clicks"] / g["clicks"].sum() * 100, 1), 0.05)
for p in ("España", "Perú"):
    x = dt[dt["property"] == p].set_index("device")
    chk(f"{p}: % impresiones móvil", D["dispositivos"][p]["MOBILE"]["pct_impr"], round(x.loc["MOBILE", "impressions"] / x["impressions"].sum() * 100, 1), 0.05)

print("\n7. Demanda no comprada (total desde los CSV de análisis)")
nc = pd.concat([pd.read_csv(os.path.join(HIST, m, "analisis", "demanda_no_comprada.csv"), encoding="utf-8-sig") for m in ("cu", "ps")])
chk("queries sin comprar: total", sum(v["queries"] for v in D["no_comprada"].values()), len(nc))
chk("queries sin comprar: impresiones", sum(v["impresiones"] for v in D["no_comprada"].values()), int(nc["impressions"].sum()))
# una a mano: iso 45001 en España con 40+ y sin keyword/término que contenga 45001
kw = pd.read_csv(os.path.join(ROOT, "datos", "ads", "Informe de palabras clave de busqueda.csv"), skiprows=2, dtype=str)
kw_es = kw[kw["Campaña"].fillna("").str.startswith("CU España")]
st_es = st[st["Campaña"].fillna("").str.startswith("CU España")]
hay = kw_es["Palabra clave"].fillna("").str.contains("45001").any() or st_es["Término de búsqueda"].fillna("").str.contains("45001").any()
chk("iso 45001 no está en las campañas de CU España (0 = no está)", 0, int(hay))

print("\n8. Interanual Argentina")
g = dcu[(dcu["property"] == "Argentina") & dcu["date"].str[:7].isin(["2025-06", "2025-07", "2025-08"])]
chk("Argentina jun-ago 2025: impresiones", D["interanual"]["Argentina"]["total"]["impr_2025"], int(g["impressions"].sum()))
g = dcu[(dcu["property"] == "Argentina") & dcu["date"].str[:7].isin(["2026-06", "2026-07", "2026-08"])]
chk("Argentina jun-ago 2026: impresiones", D["interanual"]["Argentina"]["total"]["impr_2026"], int(g["impressions"].sum()))

n_ok = sum(1 for c in checks if c[3]); n_tot = len(checks)
res = f"{n_ok} de {n_tot} coinciden" + ("" if n_ok == n_tot else " · HAY DIFERENCIAS")
print(f"\nRESULTADO: {res}")
D["verificacion"] = dict(numeros=n_tot, ok=n_ok, resultado=("los " + str(n_tot) + " coinciden" if n_ok == n_tot else res),
                         detalle=[dict(nombre=a, informe=b, fuente=c, ok=d) for a, b, c, d in checks])
json.dump(D, open(J, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
pd.DataFrame(checks, columns=["numero", "informe", "fuente", "ok"]).to_csv(os.path.join(ROOT, "informe", "verificacion.csv"), index=False, encoding="utf-8-sig")
sys.exit(0 if n_ok == n_tot else 1)
