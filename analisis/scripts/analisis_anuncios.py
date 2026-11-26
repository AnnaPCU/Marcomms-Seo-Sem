# -*- coding: utf-8 -*-
"""
analisis_anuncios.py — por grupo de anuncios con gasto: qué dice el anuncio hoy, qué buscó la gente que lo
activó (términos pagos), cómo busca el mismo tema en orgánico (Search Console) y qué títulos rinden peor.
Sale a informe/datos_anuncios.json para escribir propuestas de anuncios.
"""
import glob, json, os, re
from collections import Counter
import pandas as pd
from lib_analisis import tokens_tema, normalizar, cargar_hist, agregar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = os.path.join(ROOT, "datos", "ads", "api")
INF = os.path.join(ROOT, "informe")
W1, W2 = "2026-08-01_2026-09-11", "2026-09-12_2026-09-24"
EST = sorted(glob.glob(os.path.join(API, "estructura_*")))[-1]
PROP = {"CU España": ("cu", "España", "esp"), "CU Portugal": ("cu", "Portugal", "prt"), "CU Canada": ("cu", "Norteamérica", "can"),
        "CU United States": ("cu", "Norteamérica", "usa"), "CU Argentina": ("cu", "Argentina", "arg"), "PCU España": ("cu", "España", "esp"),
        "PCU Argentina": ("cu", "Argentina", "arg"), "PS Argentina": ("ps", "Américas", "arg")}


def load(m, r, w):
    p = os.path.join(API, m, f"ads_{m}_{r}_{w}.csv")
    return pd.read_csv(p, encoding="utf-8-sig") if os.path.exists(p) else pd.DataFrame()


an = pd.read_csv(os.path.join(EST, "anuncios.csv"), encoding="utf-8-sig"); an = an[an["ad_group_ad.status"] == "ENABLED"]
kw = pd.read_csv(os.path.join(EST, "keywords.csv"), encoding="utf-8-sig"); kw = kw[(kw["ad_group_criterion.negative"] != True) & (kw["ad_group_criterion.status"] == "ENABLED")]
rec = pd.concat([load(m, "recursos", W2) for m in ("cu", "ps", "pcu")])
rel = pd.concat([pd.read_csv(p, encoding="utf-8-sig") for p in glob.glob(os.path.join(API, "*", "analisis", f"relacion_termino_anuncio_{W2}.csv"))])
rel1 = pd.concat([pd.read_csv(p, encoding="utf-8-sig") for p in glob.glob(os.path.join(API, "*", "analisis", f"relacion_termino_anuncio_{W1}.csv"))])
ORG = {}
for m in ("cu", "ps"):
    q = cargar_hist(m, "queries_agg")
    for p in q["property"].unique():
        ORG[p] = q[q["property"] == p]

gasto = pd.concat([rel1, rel]).groupby(["campana", "grupo"])["coste"].sum().sort_values(ascending=False)
salida = []
for (c, g), coste in gasto.items():
    if coste < 8000:
        continue
    a = an[(an["campaign.name"] == c) & (an["ad_group.name"] == g)]
    if a.empty:
        continue
    pref = next((k for k in PROP if c.startswith(k)), None)
    marca, prop, pais = PROP.get(pref, (None, None, None))
    tit = [h for x in a["ad_group_ad.ad.responsive_search_ad.headlines"].dropna() for h in str(x).split(" | ")]
    des = [h for x in a["ad_group_ad.ad.responsive_search_ad.descriptions"].dropna() for h in str(x).split(" | ")]
    urls = a["ad_group_ad.ad.final_urls"].dropna().astype(str).tolist()
    fuerza = a["ad_group_ad.ad_strength"].dropna().astype(str).tolist()
    # rendimiento de títulos
    r = rec[(rec["campaign.name"] == c) & (rec["ad_group.name"] == g)]
    labels = {}
    if not r.empty and "ad_group_ad_asset_view.performance_label" in r:
        for _, x in r.iterrows():
            labels[str(x["asset.text_asset.text"])] = (str(x.get("ad_group_ad_asset_view.performance_label")), int(x.get("metrics.impressions", 0) or 0))
    # términos pagos (dos ventanas) y sus tokens no cubiertos por títulos
    t = pd.concat([rel1, rel]); t = t[(t["campana"] == c) & (t["grupo"] == g)].groupby(["termino", "relacion_anuncio"], as_index=False).agg(coste=("coste", "sum"), clics=("clics", "sum")).sort_values("coste", ascending=False)
    sq_tit = re.sub(r"[^a-z0-9]", "", normalizar(" ".join(tit)))
    tok_tit = set(tokens_tema(" ".join(tit)))
    faltan = Counter()
    for _, x in t.iterrows():
        for tk in tokens_tema(x["termino"]):
            if tk not in tok_tit and tk not in sq_tit:
                faltan[tk] += x["coste"]
    # keywords del grupo -> tema principal -> queries orgánicas
    kws = kw[(kw["campaign.name"] == c) & (kw["ad_group.name"] == g)]["ad_group_criterion.keyword.text"].astype(str).tolist()
    tk_kw = Counter(tk for k in kws for tk in tokens_tema(k))
    principal = [tk for tk, _ in tk_kw.most_common(3)]
    organico = []
    if prop in ORG and principal:
        o = ORG[prop]; o = o[o["country"] == pais] if pais else o
        o = agregar(o, ["query"])
        o = o[o["query"].map(lambda s: bool(set(tokens_tema(s)) & set(principal[:2])))].sort_values("impressions", ascending=False)
        organico = [dict(query=x["query"], impr=int(x["impressions"]), pos=float(x["position"])) for _, x in o.head(8).iterrows()]
        org_tok = Counter()
        for _, x in o.head(30).iterrows():
            for tk in tokens_tema(x["query"]):
                if tk not in tok_tit and tk not in sq_tit and tk not in principal:
                    org_tok[tk] += x["impressions"]
    else:
        org_tok = Counter()
    salida.append(dict(campana=c, grupo=g, marca=marca, propiedad=prop, coste=round(float(coste)), anuncios=len(a), fuerza=fuerza,
                       titulos=tit, descripciones=des, url=urls[0] if urls else "", labels=labels, keywords=kws[:12], tema=principal,
                       terminos=t.head(10).to_dict("records"), faltan_pago=[(k, round(v)) for k, v in faltan.most_common(8)],
                       organico=organico, faltan_organico=[(k, int(v)) for k, v in org_tok.most_common(8)]))
json.dump(salida, open(os.path.join(INF, "datos_anuncios.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
for s in salida:
    print(f"\n### {s['campana']} › {s['grupo']}  · ARS {s['coste']:,} · fuerza {s['fuerza']} · {s['anuncios']} anuncio(s)")
    print("  TÍTULOS:", " | ".join(s["titulos"])[:400])
    print("  DESC:", " | ".join(s["descripciones"])[:300])
    low = [k for k, (l, i) in s["labels"].items() if l == "LOW"]; best = [k for k, (l, i) in s["labels"].items() if l == "BEST"]
    print("  LOW:", low[:6], "| BEST:", best[:4])
    print("  TÉRMINOS:", "; ".join(f"{x['termino']} ({x['relacion_anuncio'][0]}, {x['coste']:.0f})" for x in s["terminos"][:7]))
    print("  FALTAN (pago):", s["faltan_pago"][:6], "| tema:", s["tema"])
    print("  ORGÁNICO:", "; ".join(f"{x['query']} ({x['impr']}, {x['pos']:.0f})" for x in s["organico"][:6]))
    print("  FALTAN (orgánico):", s["faltan_organico"][:6])
print(f"\n{len(salida)} grupos con 8.000+ de gasto -> informe/datos_anuncios.json")
