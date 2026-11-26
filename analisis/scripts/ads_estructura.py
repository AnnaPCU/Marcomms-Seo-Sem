# -*- coding: utf-8 -*-
"""
ads_estructura.py — foto de la ESTRUCTURA actual de la cuenta (sin métricas ni fechas):
campañas de todo tipo y estado, grupos, keywords con estado, negativos de campaña y de grupo,
anuncios activos. Sirve para saber qué existe hoy y qué cambió desde la auditoría.

Salida: datos/ads/api/estructura_<fecha>/*.csv  (por marca según prefijo CU / PS / PCU)
"""
import datetime as dt, json, os
import pandas as pd
from google.ads.googleads.client import GoogleAdsClient
from ads_export import aplanar, marca_de, YAML, CUENTAS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOY = dt.date.today()
OUT = os.path.join(ROOT, "datos", "ads", "api", f"estructura_{HOY:%Y%m%d}")

Q = {
    "campanas": """SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type,
                   campaign_budget.amount_micros, campaign.bidding_strategy_type, campaign.serving_status
                   FROM campaign ORDER BY campaign.name""",
    "grupos": """SELECT campaign.name, ad_group.id, ad_group.name, ad_group.status FROM ad_group ORDER BY campaign.name, ad_group.name""",
    "keywords": """SELECT campaign.name, ad_group.name, ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
                   ad_group_criterion.keyword.match_type, ad_group_criterion.status, ad_group_criterion.negative,
                   ad_group_criterion.final_urls, ad_group_criterion.quality_info.quality_score,
                   ad_group_criterion.quality_info.creative_quality_score, ad_group_criterion.quality_info.search_predicted_ctr,
                   ad_group_criterion.quality_info.post_click_quality_score, ad_group_criterion.system_serving_status
                   FROM ad_group_criterion WHERE ad_group_criterion.type = 'KEYWORD' ORDER BY campaign.name, ad_group.name""",
    "negativos_campana": """SELECT campaign.name, campaign_criterion.keyword.text, campaign_criterion.keyword.match_type
                   FROM campaign_criterion WHERE campaign_criterion.negative = TRUE AND campaign_criterion.type = 'KEYWORD'""",
    "anuncios": """SELECT campaign.name, ad_group.name, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.type,
                   ad_group_ad.ad.final_urls, ad_group_ad.ad.responsive_search_ad.headlines,
                   ad_group_ad.ad.responsive_search_ad.descriptions, ad_group_ad.ad_strength, ad_group_ad.policy_summary.approval_status
                   FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED' ORDER BY campaign.name, ad_group.name""",
    "listas_negativas": """SELECT shared_set.name, shared_set.type, shared_set.status, shared_criterion.keyword.text,
                   shared_criterion.keyword.match_type FROM shared_criterion WHERE shared_set.type = 'NEGATIVE_KEYWORDS'""",
    "listas_aplicadas": """SELECT campaign.name, shared_set.name FROM campaign_shared_set WHERE shared_set.type = 'NEGATIVE_KEYWORDS'""",
}


def main():
    client = GoogleAdsClient.load_from_storage(YAML)
    svc = client.get_service("GoogleAdsService")
    cid = CUENTAS["cuentas"]["principal"]
    os.makedirs(OUT, exist_ok=True)
    for nombre, gaql in Q.items():
        filas = []
        try:
            for lote in svc.search_stream(customer_id=cid, query=" ".join(gaql.split())):
                filas.extend(aplanar(r) for r in lote.results)
        except Exception as ex:
            print(f"  ! {nombre}: {str(ex)[:200]}"); continue
        df = pd.DataFrame(filas)
        if df.empty:
            print(f"  [{nombre}] 0 filas"); continue
        campo = next((c for c in df.columns if c.endswith("campaign.name")), None)
        df["marca"] = df[campo].map(marca_de) if campo else "cuenta"
        df.to_csv(os.path.join(OUT, f"{nombre}.csv"), index=False, encoding="utf-8-sig")
        print(f"  [{nombre}] {len(df):,} filas · " + " ".join(f"{m}={n}" for m, n in df["marca"].value_counts().items()))
    print("->", OUT)


if __name__ == "__main__":
    main()
