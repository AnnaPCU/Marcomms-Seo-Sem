# -*- coding: utf-8 -*-
"""verificar_estado.py — recalcula desde los CSV de la API los números principales del plan unificado."""
import glob, json, os, sys
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = os.path.join(ROOT, "datos", "ads", "api")
E = json.load(open(os.path.join(ROOT, "informe", "datos_estado.json"), encoding="utf-8"))
W1, W2 = "2026-08-01_2026-09-11", "2026-09-12_2026-09-24"
checks = []


def chk(nombre, esperado, obtenido, tol=0.5):
    ok = abs(float(esperado) - float(obtenido)) <= tol
    checks.append(ok); print(f"  {'OK ' if ok else 'XX '} {nombre:<58} informe={esperado}  fuente={obtenido}")


def kw(w):
    return pd.concat([pd.read_csv(p, encoding="utf-8-sig") for p in glob.glob(os.path.join(API, "*", f"ads_*_keywords_{w}.csv"))])


k1, k2 = kw(W1), kw(W2)
T = E["totales"]
chk("gasto por día · auditoría (42 d)", T["dia_aud"], round(k1["metrics.coste"].sum() / 42))
chk("gasto por día · 12–24 sep (13 d)", T["dia_post"], round(k2["metrics.coste"].sum() / 13))
chk("conversiones 12–24 sep", T["conv_post"], k2["metrics.conversions"].sum())
chk("conversiones auditoría (API)", T["conv_aud"], k1["metrics.conversions"].sum())
est = sorted(glob.glob(os.path.join(API, "estructura_*")))[-1]
camp = pd.read_csv(os.path.join(est, "campanas.csv"), encoding="utf-8-sig")
camp = camp[(camp["campaign.status"] != "REMOVED") & (camp["campaign.advertising_channel_type"] == "SEARCH")]
aud = pd.read_csv(os.path.join(ROOT, "datos", "ads", "Informe de palabras clave de busqueda.csv"), skiprows=2, dtype=str)
aud_c = set(aud.loc[aud["Campaña"].notna() & aud["Campaña"].str.match(r"^(CU|PS) "), "Campaña"].str.replace(r"^CU (España|Argentina) - (Competidores )?ISO 27001", r"PCU \1 - \2ISO 27001", regex=True))
chk("campañas nuevas", T["nuevas"], int((~camp["campaign.name"].isin(aud_c)).sum()))
chk("campañas de búsqueda activas", T["campanas"], len(camp))
for nombre in ["PCU España - ISO 27001 - Search", "PCU Argentina - ISO 27001 - Search", "CU United States - Organic - USDA NOP - Search", "CU España - Smeta - Search", "PS Argentina - SuSe - Huella de agua - Search", "CU Canada - Forestry - Search"]:
    c = next(x for x in E["campanas"] if x["campana"] == nombre)
    chk(f"{nombre[:40]}: gasto/día ahora", c["coste_dia_post"], round(k2.loc[k2["campaign.name"] == nombre, "metrics.coste"].sum() / 13))
    chk(f"{nombre[:40]}: gasto/día auditoría", c["coste_dia_aud"], round(k1.loc[k1["campaign.name"] == nombre, "metrics.coste"].sum() / 42))
# relación SMETA España nula 80%
r = pd.read_csv(os.path.join(API, "cu", "analisis", f"relacion_termino_anuncio_{W2}.csv"), encoding="utf-8-sig")
g = r[r["campana"] == "CU España - Smeta - Search"]
chk("SMETA España: % gasto con anuncio nulo", next(x for x in E["campanas"] if x["campana"] == "CU España - Smeta - Search")["rel_post"]["pct_nula"], round(g.loc[g["relacion_anuncio"] == "nula", "coste"].sum() / g["coste"].sum() * 100, 1))
# negativos aplicados: CAEs 0 de 6
neg = pd.read_csv(os.path.join(est, "negativos_campana.csv"), encoding="utf-8-sig")
cae = neg[neg["campaign.name"].str.startswith("CU España - CAEs")]["campaign_criterion.keyword.text"].str.lower()
chk("CAEs: negativos de vivienda aplicados (0)", 0, int(cae.str.contains("vivienda|particular|gratis|ce3x|certicalia").sum()))
print(f"\nRESULTADO: {sum(checks)} de {len(checks)} coinciden")
sys.exit(0 if all(checks) else 1)
