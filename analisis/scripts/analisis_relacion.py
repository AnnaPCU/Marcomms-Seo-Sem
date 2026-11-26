# -*- coding: utf-8 -*-
"""
analisis_relacion.py — qué tan relacionado está el anuncio con el término de búsqueda.

Para cada término de búsqueda con gasto: la keyword que lo activó, el grupo de anuncios, los anuncios
RSA de ese grupo (títulos, descripciones, URL final) y el nivel de calidad de la keyword. Se mide:

  relacion_anuncio   ¿los tokens-tema del término aparecen en algún título del grupo?
                     fuerte = todos · parcial = alguno · nula = ninguno
  relacion_landing   ¿la URL final del anuncio contiene el tema del término?
  google_relevancia  «Relevancia del anuncio» que Google asigna a la keyword (por encima / media / por debajo)
  score 0–3          fuerte + landing + relevancia ≥ media

Fuente: datos/ads/api/<marca>/ (extracción por API). Salida por marca:
  datos/ads/api/<marca>/analisis/relacion_termino_anuncio.csv
  informe/datos_relacion.json  (resumen por campaña y ejemplos)
"""
import glob, json, os, re, sys
import pandas as pd
from lib_analisis import tokens_tema, normalizar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = os.path.join(ROOT, "datos", "ads", "api")
INF = os.path.join(ROOT, "informe")
W = sys.argv[1] if len(sys.argv) > 1 else "2026-08-01_2026-09-11"
MARCAS = ["cu", "ps", "pcu"]
QS = {"ABOVE_AVERAGE": "por encima", "AVERAGE": "media", "BELOW_AVERAGE": "por debajo"}


def load(m, r):
    p = os.path.join(API, m, f"ads_{m}_{r}_{W}.csv")
    return pd.read_csv(p, encoding="utf-8-sig") if os.path.exists(p) else pd.DataFrame()


def squash(s):
    return re.sub(r"[^a-z0-9]", "", normalizar(str(s)))


def coincide(tema, tokens, texto_squash):
    """tokens del término presentes en los tokens del texto, o pegados dentro del texto sin espacios
    (canada gap ~ CanadaGAP · iso27001 ~ ISO 27001 · global gap ~ GLOBALG.A.P.)"""
    return sum(1 for t in tema if t in tokens or (len(t) >= 3 and t in texto_squash))


def slug_tokens(url):
    return tokens_tema(re.sub(r"^https?://[^/]+", "", str(url)).replace("-", " ").replace("/", " "))


R = {"ventana": W, "marcas": {}}
for m in MARCAS:
    t, k, a = load(m, "terminos"), load(m, "keywords"), load(m, "anuncios")
    if t.empty:
        continue
    # anuncios activos por grupo: títulos, descripciones y URL final concatenados
    a = a[a["ad_group_ad.status"] == "ENABLED"] if "ad_group_ad.status" in a else a
    grupos = {}
    for (c, g), x in a.groupby(["campaign.name", "ad_group.name"]):
        titulos = " | ".join(x["ad_group_ad.ad.responsive_search_ad.headlines"].dropna().astype(str))
        descs = " | ".join(x["ad_group_ad.ad.responsive_search_ad.descriptions"].dropna().astype(str)) if "ad_group_ad.ad.responsive_search_ad.descriptions" in x else ""
        urls = x["ad_group_ad.ad.final_urls"].dropna().astype(str).tolist() if "ad_group_ad.ad.final_urls" in x else []
        grupos[(c, g)] = dict(titulos=titulos, descs=descs, url=(urls[0] if urls else ""),
                              tok_titulos=set(tokens_tema(titulos)), tok_descs=set(tokens_tema(descs)),
                              sq_titulos=squash(titulos), sq_descs=squash(descs),
                              tok_url=set(slug_tokens(urls[0])) if urls else set(), n_anuncios=len(x))
    # nivel de calidad por keyword (campaña, grupo, texto)
    kq = {}
    for _, r in k.iterrows():
        kq[(r["campaign.name"], r["ad_group.name"], normalizar(str(r["ad_group_criterion.keyword.text"])))] = dict(
            qs=r.get("ad_group_criterion.quality_info.quality_score"),
            relev=QS.get(r.get("ad_group_criterion.quality_info.creative_quality_score"), None),
            ctr_esp=QS.get(r.get("ad_group_criterion.quality_info.search_predicted_ctr"), None),
            landing=QS.get(r.get("ad_group_criterion.quality_info.post_click_quality_score"), None))
    filas = []
    for _, r in t.iterrows():
        if r["metrics.coste"] <= 0 and r["metrics.clicks"] <= 0:
            continue
        term = str(r["search_term_view.search_term"]); tema = set(tokens_tema(term))
        g = grupos.get((r["campaign.name"], r["ad_group.name"]))
        kw = normalizar(str(r.get("segments.keyword.info.text", "")))
        q = kq.get((r["campaign.name"], r["ad_group.name"], kw), {})
        if g is None or not tema:
            rel_anuncio, en_titulo, en_desc, rel_landing = "sin anuncio", 0, 0, None
        else:
            en_titulo = coincide(tema, g["tok_titulos"], g["sq_titulos"]); en_desc = coincide(tema, g["tok_descs"], g["sq_descs"])
            rel_anuncio = "fuerte" if en_titulo == len(tema) else ("parcial" if en_titulo or en_desc else "nula")
            rel_landing = (coincide(tema, g["tok_url"], squash(g["url"])) > 0) if g["url"] else None
        score = (rel_anuncio == "fuerte") + (rel_landing is True) + (q.get("relev") in ("media", "por encima"))
        filas.append(dict(marca=m.upper(), campana=r["campaign.name"], grupo=r["ad_group.name"], termino=term, keyword=kw,
                          concordancia=r.get("segments.keyword.info.match_type"), clics=int(r["metrics.clicks"]), impr=int(r["metrics.impressions"]),
                          coste=round(float(r["metrics.coste"]), 2), conv=float(r.get("metrics.conversions", 0) or 0),
                          relacion_anuncio=rel_anuncio, tokens_termino=len(tema), tokens_en_titulo=en_titulo, tokens_en_descripcion=en_desc,
                          relacion_landing=rel_landing, google_qs=q.get("qs"), google_relevancia=q.get("relev"), google_ctr_esperado=q.get("ctr_esp"),
                          google_landing=q.get("landing"), score=score, titulos=(g["titulos"][:300] if g else ""), url_final=(g["url"] if g else "")))
    df = pd.DataFrame(filas).sort_values("coste", ascending=False)
    out = os.path.join(API, m, "analisis"); os.makedirs(out, exist_ok=True)
    df.to_csv(os.path.join(out, f"relacion_termino_anuncio_{W}.csv"), index=False, encoding="utf-8-sig")
    # resumen
    tot = df["coste"].sum()
    por_rel = df.groupby("relacion_anuncio").agg(coste=("coste", "sum"), terminos=("termino", "count"), clics=("clics", "sum"))
    por_rel["pct"] = (por_rel["coste"] / tot * 100).round(1)
    por_camp = df.groupby("campana").apply(lambda x: pd.Series(dict(
        coste=x["coste"].sum(), terminos=len(x), clics=x["clics"].sum(),
        pct_nula=x.loc[x["relacion_anuncio"] == "nula", "coste"].sum() / x["coste"].sum() * 100 if x["coste"].sum() else 0,
        pct_fuerte=x.loc[x["relacion_anuncio"] == "fuerte", "coste"].sum() / x["coste"].sum() * 100 if x["coste"].sum() else 0,
        score_medio=(x["score"] * x["coste"]).sum() / x["coste"].sum() if x["coste"].sum() else 0,
        relev_debajo=x.loc[x["google_relevancia"] == "por debajo", "coste"].sum()))).round(1).sort_values("coste", ascending=False).reset_index()
    peores = df[df["relacion_anuncio"] == "nula"].head(12)[["campana", "termino", "keyword", "coste", "clics", "titulos", "url_final"]]
    mejores = df[df["relacion_anuncio"] == "fuerte"].head(6)[["campana", "termino", "keyword", "coste", "clics"]]
    R["marcas"][m] = dict(coste_total=round(tot), terminos=len(df), por_relacion=por_rel.reset_index().to_dict("records"),
                         por_campana=por_camp.to_dict("records"), peores=peores.to_dict("records"), mejores=mejores.to_dict("records"),
                         google=dict(con_dato=int(df["google_relevancia"].notna().sum()),
                                     coste_relev_debajo=round(df.loc[df["google_relevancia"] == "por debajo", "coste"].sum()),
                                     coste_landing_debajo=round(df.loc[df["google_landing"] == "por debajo", "coste"].sum())))
    print(f"\n===== {m.upper()} · {len(df)} términos con gasto/clic · ARS {tot:,.0f}")
    print(por_rel.to_string())
    print("\nPor campaña (coste, % nula, % fuerte, score medio 0-3, coste con relevancia 'por debajo'):")
    print(por_camp[["campana", "coste", "pct_nula", "pct_fuerte", "score_medio", "relev_debajo"]].to_string(index=False))
    print("\nPeores (relación nula, más gasto):")
    for _, x in peores.head(8).iterrows():
        print(f"  ARS {x['coste']:>8,.0f}  «{x['termino']}»  ← kw «{x['keyword']}»  [{x['campana'][:34]}]  títulos: {x['titulos'][:90]}")
json.dump(R, open(os.path.join(INF, f"datos_relacion_{W}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("\n-> informe/datos_relacion.json")
