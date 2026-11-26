# -*- coding: utf-8 -*-
"""
ficha_campana.py — radiografía de una campaña para escribir o revisar una tarjeta del tablero: grupos, keywords (con
nivel de calidad y gasto), negativas de campaña y de grupo, anuncios activos (títulos, descripciones, URL, fuerza) con
el rendimiento de cada recurso, y términos de búsqueda con gasto. Lee el último snapshot de estructura y la ventana
de reportes más reciente de datos/ads/api.

Uso: python ficha_campana.py "CU Argentina - Biocombustible - Search" [--terminos 40]
"""
import argparse, glob, os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = os.path.join(ROOT, "datos", "ads", "api")


def leer(patron):
    fs = sorted(glob.glob(os.path.join(API, patron)))
    return pd.concat([pd.read_csv(f, encoding="utf-8-sig") for f in fs], ignore_index=True) if fs else pd.DataFrame()


def ultima_ventana():
    fs = sorted(glob.glob(os.path.join(API, "*", "ads_*_terminos_*.csv")), key=os.path.getmtime)
    return "_".join(os.path.basename(fs[-1]).split("_")[-2:]).replace(".csv", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("campana")
    ap.add_argument("--terminos", type=int, default=40)
    a = ap.parse_args()
    snap = sorted(glob.glob(os.path.join(API, "estructura_*")))[-1]
    v = ultima_ventana()
    est = lambda f: pd.read_csv(os.path.join(snap, f), encoding="utf-8-sig")
    c = est("campanas.csv")
    c = c[c["campaign.name"] == a.campana]
    if c.empty:
        raise SystemExit(f"No está «{a.campana}» en {os.path.basename(snap)}")
    r = c.iloc[0]
    print(f"# {a.campana} · {r['campaign.status']} · {r['campaign.serving_status']} · puja {r['campaign.bidding_strategy_type']} · "
          f"presupuesto ARS {r['campaign_budget.amount_micros'] / 1e6:,.0f}/día · estructura {os.path.basename(snap)} · métricas {v}")

    g = est("grupos.csv")
    g = g[g["campaign.name"] == a.campana]
    kw = est("keywords.csv")
    kw = kw[kw["campaign.name"] == a.campana]
    kwm = leer(f"*/ads_*_keywords_{v}.csv")
    kwm = kwm[kwm["campaign.name"] == a.campana] if not kwm.empty else kwm
    an = est("anuncios.csv")
    an = an[an["campaign.name"] == a.campana]
    anm = leer(f"*/ads_*_anuncios_{v}.csv")
    rec = leer(f"*/ads_*_recursos_{v}.csv")
    neg = est("negativos_campana.csv")
    neg = neg[neg["campaign.name"] == a.campana]

    for _, gr in g.iterrows():
        nombre = gr["ad_group.name"]
        print(f"\n## Grupo «{nombre}» · {gr['ad_group.status']} · id {gr['ad_group.id']}")
        k = kw[(kw["ad_group.name"] == nombre)]
        pos, negs = k[k["ad_group_criterion.negative"] != True], k[k["ad_group_criterion.negative"] == True]  # noqa: E712
        print("  Keywords:")
        for _, x in pos.iterrows():
            m = kwm[(kwm["ad_group.name"] == nombre) & (kwm["ad_group_criterion.keyword.text"] == x["ad_group_criterion.keyword.text"]) &
                    (kwm["ad_group_criterion.keyword.match_type"] == x["ad_group_criterion.keyword.match_type"])] if not kwm.empty else pd.DataFrame()
            gasto = f" · {int(m['metrics.clicks'].sum())} clics ARS {m['metrics.cost_micros'].sum() / 1e6:,.0f}" if not m.empty else ""
            qs = x["ad_group_criterion.quality_info.quality_score"]
            print(f"    [{x['ad_group_criterion.keyword.match_type']}] {x['ad_group_criterion.keyword.text']} · {x['ad_group_criterion.status']}"
                  f"{'' if pd.isna(qs) else f' · QS {int(qs)}'}{gasto}")
        if len(negs):
            print("  Negativas del grupo: " + ", ".join(f"[{x['ad_group_criterion.keyword.match_type']}] {x['ad_group_criterion.keyword.text']}" for _, x in negs.iterrows()))
        for _, ad in an[an["ad_group.name"] == nombre].iterrows():
            m = anm[anm["ad_group_ad.ad.id"] == ad["ad_group_ad.ad.id"]] if not anm.empty else pd.DataFrame()
            gasto = f" · {int(m['metrics.clicks'].sum())} clics ARS {m['metrics.cost_micros'].sum() / 1e6:,.0f}" if not m.empty else ""
            print(f"  Anuncio id {ad['ad_group_ad.ad.id']} · {ad['ad_group_ad.status']} · fuerza {ad['ad_group_ad.ad_strength']} · {ad['ad_group_ad.policy_summary.approval_status']}{gasto}")
            print(f"    URL: {ad['ad_group_ad.ad.final_urls']}")
            rr = rec[rec["ad_group_ad.ad.id"] == ad["ad_group_ad.ad.id"]] if not rec.empty else pd.DataFrame()
            for campo, col in (("Títulos", "ad_group_ad.ad.responsive_search_ad.headlines"), ("Descripciones", "ad_group_ad.ad.responsive_search_ad.descriptions")):
                print(f"    {campo}: {ad[col]}")
            if not rr.empty:
                print("    Rendimiento de recursos: " + " | ".join(f"{t} [{p}]" for t, p in rr.groupby("asset.text_asset.text")["ad_group_ad_asset_view.performance_label"].first().items()))
    if len(neg):
        print("\n## Negativas de campaña: " + ", ".join(f"[{x['campaign_criterion.keyword.match_type']}] {x['campaign_criterion.keyword.text']}" for _, x in neg.iterrows()))
    else:
        print("\n## Negativas de campaña: ninguna")

    t = leer(f"*/ads_*_terminos_{v}.csv")
    t = t[t["campaign.name"] == a.campana]
    if not t.empty:
        t = t.groupby(["search_term_view.search_term", "ad_group.name", "segments.keyword.info.text"], dropna=False).agg(
            clics=("metrics.clicks", "sum"), impr=("metrics.impressions", "sum"), coste=("metrics.cost_micros", "sum"), conv=("metrics.conversions", "sum")).reset_index()
        t["coste"] = t["coste"] / 1e6
        print(f"\n## Términos de búsqueda ({v}) · {len(t)} términos · ARS {t['coste'].sum():,.0f} · {int(t['clics'].sum())} clics")
        for _, x in t.sort_values(["coste", "impr"], ascending=False).head(a.terminos).iterrows():
            print(f"  {x['search_term_view.search_term']} · grupo {x['ad_group.name']} · kw «{x['segments.keyword.info.text']}» · {int(x['impr'])} impr · {int(x['clics'])} clics · ARS {x['coste']:,.0f} · conv {x['conv']:.0f}")


if __name__ == "__main__":
    main()
