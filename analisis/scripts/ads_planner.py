# -*- coding: utf-8 -*-
"""
ads_planner.py — Planificador de palabras clave por API (solo lectura, no toca la cuenta).

  historico  volumen mensual, competencia y rango de puja (parte superior de la página) de una lista de keywords
  ideas      ideas nuevas a partir de semillas y/o una URL

Uso:
  python ads_planner.py historico --geo 2840,2484,2124 --idioma 1000 --kw "ifpa 2026" "gpfs 2026" --sal archivo.csv
  python ads_planner.py ideas --geo 2840 --kw "primusgfs certification" --url https://... --sal archivo.csv
Geo: 2840 EE.UU., 2484 México, 2124 Canadá. Idioma: 1000 inglés, 1003 español.
Los montos salen en la moneda de la cuenta (ARS).
"""
import argparse, json, os, sys
import pandas as pd
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CID = json.load(open(os.path.join(ROOT, "google-ads.cuentas.json"), encoding="utf-8"))["cuentas"]["principal"]


def fila(texto, m):
    meses = {f"{x.year}-{x.month.value - 1 if hasattr(x.month, 'value') else x.month:02d}": x.monthly_searches for x in m.monthly_search_volumes} if m.monthly_search_volumes else {}
    return dict(keyword=texto, busquedas_mes=m.avg_monthly_searches, competencia=m.competition.name, indice_comp=m.competition_index,
                puja_baja=round(m.low_top_of_page_bid_micros / 1e6), puja_alta=round(m.high_top_of_page_bid_micros / 1e6),
                meses=json.dumps(meses))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["historico", "ideas"])
    ap.add_argument("--geo", default="2840")
    ap.add_argument("--idioma", default="1000")
    ap.add_argument("--kw", nargs="*", default=[])
    ap.add_argument("--url")
    ap.add_argument("--sal", required=True)
    a = ap.parse_args()
    client = GoogleAdsClient.load_from_storage(os.path.join(ROOT, "google-ads.yaml"))
    svc = client.get_service("KeywordPlanIdeaService")
    geos = [client.get_service("GeoTargetConstantService").geo_target_constant_path(g) for g in a.geo.split(",")]
    idioma = client.get_service("GoogleAdsService").language_constant_path(a.idioma)
    filas = []
    try:
        if a.modo == "historico":
            req = client.get_type("GenerateKeywordHistoricalMetricsRequest")
            req.customer_id = CID
            req.keywords.extend(a.kw)
            req.geo_target_constants.extend(geos)
            req.language = idioma
            req.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
            for r in svc.generate_keyword_historical_metrics(request=req).results:
                filas.append(fila(r.text, r.keyword_metrics) | {"variantes": " | ".join(r.close_variants)})
        else:
            req = client.get_type("GenerateKeywordIdeasRequest")
            req.customer_id = CID
            req.language = idioma
            req.geo_target_constants.extend(geos)
            req.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
            if a.kw and a.url:
                req.keyword_and_url_seed.keywords.extend(a.kw); req.keyword_and_url_seed.url = a.url
            elif a.kw:
                req.keyword_seed.keywords.extend(a.kw)
            else:
                req.url_seed.url = a.url
            for r in svc.generate_keyword_ideas(request=req):
                filas.append(fila(r.text, r.keyword_idea_metrics))
    except GoogleAdsException as ex:
        sys.exit("Google Ads API: " + "; ".join(e.message for e in ex.failure.errors))
    pd.DataFrame(filas).to_csv(a.sal, index=False, encoding="utf-8-sig")
    print(f"{len(filas)} filas -> {a.sal}")


if __name__ == "__main__":
    main()
