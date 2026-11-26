# -*- coding: utf-8 -*-
"""
verificar_ejecutivos.py — recalcula desde los CSV fuente (sin pasar por analisis_ejecutivo.py)
los números principales de los informes «Pain points por unidad» y «Recomendaciones SEO».
"""
import json, os, re, sys, unicodedata
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST = os.path.join(ROOT, "datos", "gsc-historico")
INF = os.path.join(ROOT, "informe")
C = json.load(open(os.path.join(INF, "datos_clientes.json"), encoding="utf-8"))
S = json.load(open(os.path.join(INF, "datos_seo.json"), encoding="utf-8"))
U = {(c["propiedad"], c["pais"]): c for c in C["clientes"]}
checks = []


def chk(nombre, esperado, obtenido, tol=0):
    if isinstance(esperado, str) or isinstance(obtenido, str):
        ok = str(esperado) == str(obtenido)
    else:
        ok = esperado is not None and obtenido is not None and abs(float(esperado) - float(obtenido)) <= tol
    checks.append((nombre, esperado, obtenido, ok))
    print(f"  {'OK ' if ok else 'XX '} {nombre:<60} informe={esperado}  fuente={obtenido}")


def h(m, c):
    return pd.read_csv(os.path.join(HIST, m, f"gsc_{m}_hist_{c}.csv"), encoding="utf-8-sig", dtype={"query": str, "page": str})


def num(s):
    return float(str(s).replace(".", "").replace(",", ".")) if str(s) not in ("nan", " --", "") else 0.0


print("\n1. Ads por unidad (informe de keywords)")
kw = pd.read_csv(os.path.join(ROOT, "datos", "ads", "Informe de palabras clave de busqueda.csv"), skiprows=2, dtype=str)
kw = kw[kw["Campaña"].notna() & kw["Campaña"].str.match(r"^(CU|PS) ")]
kw["coste"] = kw["Coste"].map(num); kw["clics"] = kw["Interacciones"].map(lambda s: int(str(s).replace(".", "")) if str(s).replace(".", "").isdigit() else 0)
kw["conv"] = kw["Conversiones"].map(num)
for pref, key in (("CU España", ("España", "esp")), ("CU Canada", ("Norteamérica", "can")), ("CU United States", ("Norteamérica", "usa")),
                  ("CU Argentina", ("Argentina", "arg")), ("PS Argentina", ("Américas", "arg")), ("CU Portugal", ("Portugal", "prt"))):
    k = kw[kw["Campaña"].str.startswith(pref)]
    chk(f"{pref}: gasto", U[key]["ads"]["gasto"], round(k["coste"].sum()))
    chk(f"{pref}: clics", U[key]["ads"]["clics"], int(k["clics"].sum()))
    chk(f"{pref}: conversiones", U[key]["ads"]["conv"], int(k["conv"].sum()))
chk("gasto total", C["ads_total"], round(kw["coste"].sum()))

print("\n2. Orgánico por unidad, ventana de Ads, país de compra (baseline ads queries)")
for m, key in (("cu", ("España", "esp")), ("cu", ("Argentina", "arg")), ("cu", ("Norteamérica", "can")), ("ps", ("Américas", "arg"))):
    b = pd.read_csv(os.path.join(ROOT, "datos", "gsc", f"gsc_{m}_ads_queries.csv"), encoding="utf-8-sig")
    b = b[(b["property"] == key[0]) & (b["country"] == key[1])]
    chk(f"{key[0]}/{key[1]}: impresiones orgánicas 6 sem.", U[key]["gsc"]["impr_ads"], int(b["impressions"].sum()))
    chk(f"{key[0]}/{key[1]}: clics orgánicos 6 sem.", U[key]["gsc"]["clics_ads"], int(b["clicks"].sum()))

print("\n3. SEO: totales y umbrales")
qa = pd.concat([h("cu", "queries_agg"), h("ps", "queries_agg")])
am = qa[qa["property"] == "Américas"]; tot = am["impressions"].sum(); arg = am.loc[am["country"] == "arg", "impressions"].sum()
chk("Américas: % impresiones desde Argentina", S["Américas"]["pct_pais"], round(arg / tot * 100))
na = qa[qa["property"] == "Norteamérica"]
chk("Norteamérica: impresiones desde Canadá", 2251, int(na.loc[na["country"] == "can", "impressions"].sum()))
chk("Norteamérica: impresiones desde India", 7599, int(na.loc[na["country"] == "ind", "impressions"].sum()))
pg = pd.concat([h("cu", "pages"), h("ps", "pages")]).groupby(["property", "page"])[["clicks", "impressions"]].sum().reset_index()
chk("páginas totales", sum(v["paginas_total"] for v in S.values()), len(pg))
chk("páginas con clic", sum(v["paginas_con_clic"] for v in S.values()), int((pg["clicks"] > 0).sum()))
# CTR bajo: 1000+ impr, pos<=10, ctr<0.6% (posición ponderada por impresiones)
pgp = pd.concat([h("cu", "pages"), h("ps", "pages")])
pgp["pw"] = pgp["position"] * pgp["impressions"]
g = pgp.groupby(["property", "page"]).agg(clicks=("clicks", "sum"), impressions=("impressions", "sum"), pw=("pw", "sum")).reset_index()
g["pos"] = (g["pw"] / g["impressions"]).round(2); g["ctr"] = (g["clicks"] / g["impressions"] * 100).round(2)
low = g[(g["impressions"] >= 1000) & (g["pos"] <= 10) & (g["ctr"] < 0.6)]
n_low_inf = sum(len(v["low_ctr"]) for v in S.values())
chk("páginas con CTR bajo (informe muestra hasta 6 por sitio)", n_low_inf, int(min(len(low[low["property"] == p]), 6) for p in S) if False else sum(min(int((low["property"] == p).sum()), 6) for p in S))
# GRS México
x = g[(g["property"] == "México") & (g["page"] == "https://mexico.controlunion.com/programa-de-certificacion/grs-global-recycled-standard/")]
chk("México GRS página: impresiones", next(y["impr"] for y in S["México"]["low_ctr"] if "grs" in y["path"]), int(x["impressions"].sum()))
# TEMO Norteamérica página
x = g[(g["property"] == "Norteamérica") & g["page"].str.contains("temo-temperature")]
chk("Norteamérica TEMO página: impresiones", next(y["impr"] for y in S["Norteamérica"]["low_ctr"] if "temo" in y["path"]), int(x["impressions"].sum()))
# quick win iso 45001 España, país esp
e = qa[(qa["property"] == "España") & (qa["country"] == "esp") & (qa["query"] == "iso 45001")]
chk("España quick win iso 45001: impresiones desde ESP", next(y["impr"] for y in S["España"]["quick_wins"] if y["query"] == "iso 45001"), int(e["impressions"].sum()))
chk("España quick win iso 45001: posición ESP", next(y["pos"] for y in S["España"]["quick_wins"] if y["query"] == "iso 45001"), round(float(e["position"].iloc[0]), 2), 0.01)
# canibalización gmp+ España: dos páginas
qp = h("cu", "query_page"); x = qp[(qp["property"] == "España") & (qp["query"] == "gmp+")].sort_values("impressions", ascending=False)
chk("España gmp+: impresiones repartidas", next(c["impr"] for c in S["España"]["canibalizacion"] if c["query"] == "gmp+"), int(x["impressions"].sum()))
chk("España gmp+: página principal impr.", next(c["paginas"][0]["impr"] for c in S["España"]["canibalizacion"] if c["query"] == "gmp+"), int(x["impressions"].iloc[0]))
# pérdida deposito fiscal Argentina: 801 -> 1
q = h("cu", "queries"); q = q[(q["property"] == "Argentina") & (q["country"] == "arg") & (q["query"] == "deposito fiscal")]
a1 = q[q["date"].str[:7].isin(["2025-06", "2025-07", "2025-08"])]["impressions"].sum(); a2 = q[q["date"].str[:7].isin(["2026-06", "2026-07", "2026-08"])]["impressions"].sum()
chk("Argentina deposito fiscal: antes", next(y["antes"] for y in S["Argentina"]["perdidas"] if y["query"] == "deposito fiscal"), int(a1))
chk("Argentina deposito fiscal: después", next(y["despues"] for y in S["Argentina"]["perdidas"] if y["query"] == "deposito fiscal"), int(a2))
# PDF MSC Perú
x = g[(g["property"] == "Perú") & g["page"].str.contains("MSC-General")]
chk("Perú PDF MSC: impresiones (32.767)", 32767, int(x["impressions"].sum()))

n_ok = sum(1 for c in checks if c[3]); n_tot = len(checks)
print(f"\nRESULTADO: {n_ok} de {n_tot} coinciden")
pd.DataFrame(checks, columns=["numero", "informe", "fuente", "ok"]).to_csv(os.path.join(INF, "verificacion_ejecutivos.csv"), index=False, encoding="utf-8-sig")
sys.exit(0 if n_ok == n_tot else 1)
