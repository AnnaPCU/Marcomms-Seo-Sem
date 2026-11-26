# -*- coding: utf-8 -*-
"""
ads_export.py — extracción mensual de Google Ads por API (solo lectura), cuatro reportes:

  terminos     search_term_view      término, keyword que lo activó, campaña, grupo, clics, impr., coste, conv.
  keywords     keyword_view          keyword, concordancia, URL final, nivel de calidad y sus tres componentes
  anuncios     ad_group_ad           RSA: títulos, descripciones, URL final, estado, métricas
  recursos     ad_group_ad_asset_view  rendimiento de cada título/descripción (texto, tipo, calificación)

Uso:
  python ads_export.py --test                       una consulta chica para comprobar acceso
  python ads_export.py --desde 2026-08-01 --hasta 2026-09-11
  python ads_export.py                              por defecto, los últimos 42 días cerrados

Salida: datos/ads/api/<marca>/ads_<marca>_<reporte>_<desde>_<hasta>.csv, separada por marca según el
prefijo de la campaña (CU / PS): nunca un archivo común. Log JSONL por corrida.
"""
import argparse, csv, datetime as dt, json, os, sys
import pandas as pd
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YAML = os.path.join(ROOT, "google-ads.yaml")
CUENTAS = json.load(open(os.path.join(ROOT, "google-ads.cuentas.json"), encoding="utf-8"))
OUT = os.path.join(ROOT, "datos", "ads", "api")
HOY = dt.date.today()

QUERIES = {
    "terminos": """
        SELECT segments.search_term_match_type, search_term_view.search_term, search_term_view.status,
               segments.keyword.info.text, segments.keyword.info.match_type,
               campaign.name, ad_group.name,
               metrics.clicks, metrics.impressions, metrics.ctr, metrics.average_cpc, metrics.cost_micros,
               metrics.conversions, metrics.cost_per_conversion
        FROM search_term_view WHERE segments.date BETWEEN '{a}' AND '{b}' AND campaign.advertising_channel_type = 'SEARCH'
        ORDER BY metrics.cost_micros DESC""",
    "keywords": """
        SELECT campaign.name, ad_group.name, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
               ad_group_criterion.status, ad_group_criterion.final_urls,
               ad_group_criterion.quality_info.quality_score, ad_group_criterion.quality_info.creative_quality_score,
               ad_group_criterion.quality_info.search_predicted_ctr, ad_group_criterion.quality_info.post_click_quality_score,
               metrics.clicks, metrics.impressions, metrics.cost_micros, metrics.conversions
        FROM keyword_view WHERE segments.date BETWEEN '{a}' AND '{b}' AND campaign.advertising_channel_type = 'SEARCH'
        ORDER BY metrics.cost_micros DESC""",
    "anuncios": """
        SELECT campaign.name, ad_group.name, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.type,
               ad_group_ad.ad.final_urls, ad_group_ad.ad.responsive_search_ad.headlines,
               ad_group_ad.ad.responsive_search_ad.descriptions, ad_group_ad.ad.responsive_search_ad.path1,
               ad_group_ad.ad.responsive_search_ad.path2, ad_group_ad.ad_strength,
               metrics.clicks, metrics.impressions, metrics.cost_micros, metrics.conversions
        FROM ad_group_ad WHERE segments.date BETWEEN '{a}' AND '{b}' AND campaign.advertising_channel_type = 'SEARCH'
        ORDER BY metrics.impressions DESC""",
    "recursos": """
        SELECT campaign.name, ad_group.name, ad_group_ad.ad.id, ad_group_ad_asset_view.field_type,
               asset.text_asset.text, ad_group_ad_asset_view.performance_label, ad_group_ad_asset_view.enabled,
               metrics.impressions, metrics.clicks
        FROM ad_group_ad_asset_view WHERE segments.date BETWEEN '{a}' AND '{b}'
        ORDER BY metrics.impressions DESC""",
}


def marca_de(campana):
    c = str(campana)
    # acepta los formatos de nombre «CU España - …», «CUC USA - …» (nombre de Control Union en Estados Unidos
    # desde nov 2026) y el estándar del equipo «CU_US_SEARCH_…»
    return "cu" if c.startswith(("CU ", "CU_", "CUC ", "CUC_")) else ("ps" if c.startswith(("PS ", "PS_")) else ("pcu" if c.startswith(("PCU ", "PCU_")) else "otros"))


def aplanar(row):
    """convierte una fila GoogleAdsRow en dict plano con claves punteadas; listas de assets a texto con ' | '"""
    from google.protobuf.json_format import MessageToDict
    d = MessageToDict(row._pb, preserving_proto_field_name=True)
    plano = {}

    def rec(obj, prefijo):
        for k, v in obj.items():
            nombre = f"{prefijo}.{k}" if prefijo else k
            if isinstance(v, dict):
                rec(v, nombre)
            elif isinstance(v, list):
                if v and isinstance(v[0], dict):
                    plano[nombre] = " | ".join(str(x.get("text", x)) for x in v)
                else:
                    plano[nombre] = " | ".join(str(x) for x in v)
            else:
                plano[nombre] = v
    rec(d, "")
    return plano


def consultar(client, customer_id, gaql, log):
    svc = client.get_service("GoogleAdsService")
    filas = []
    try:
        for lote in svc.search_stream(customer_id=customer_id, query=gaql):
            for r in lote.results:
                filas.append(aplanar(r))
        log(status="ok", filas=len(filas))
    except GoogleAdsException as ex:
        detalle = "; ".join(e.message for e in ex.failure.errors)
        log(status="error", error=detalle)
        print("  ! Google Ads API:", detalle)
    return filas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--desde"); ap.add_argument("--hasta")
    a = ap.parse_args()
    if "PEGAR_AQUI" in open(YAML, encoding="utf-8").read() or "SE_GENERA" in open(YAML, encoding="utf-8").read():
        sys.exit("google-ads.yaml incompleto: falta el developer token o el refresh token (scripts/ads_auth.py).")
    client = GoogleAdsClient.load_from_storage(YAML)
    cid = CUENTAS["cuentas"]["principal"]
    os.makedirs(OUT, exist_ok=True)
    hasta = dt.date.fromisoformat(a.hasta) if a.hasta else HOY - dt.timedelta(days=1)
    desde = dt.date.fromisoformat(a.desde) if a.desde else hasta - dt.timedelta(days=41)
    logp = os.path.join(OUT, f"log_ads_{HOY:%Y%m%d}.jsonl")

    def log(**kw):
        kw["ts"] = dt.datetime.now().isoformat(timespec="seconds")
        open(logp, "a", encoding="utf-8").write(json.dumps(kw, ensure_ascii=False) + "\n")

    if a.test:
        q = "SELECT customer.id, customer.descriptive_name, customer.currency_code, customer.time_zone FROM customer LIMIT 1"
        filas = consultar(client, cid, q, lambda **k: log(reporte="test", **k))
        print("Acceso OK:" if filas else "Sin acceso.", filas[:1])
        return

    print(f"Google Ads · cuenta {cid} · {desde} → {hasta}")
    for nombre, gaql in QUERIES.items():
        q = gaql.format(a=desde, b=hasta)
        print(f"  [{nombre}]", end=" ")
        filas = consultar(client, cid, q, lambda **k: log(reporte=nombre, desde=str(desde), hasta=str(hasta), **k))
        if not filas:
            print("sin filas"); continue
        df = pd.DataFrame(filas)
        for col in [c for c in df.columns if c.startswith("metrics.")]:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass
        for col in [c for c in df.columns if c.endswith("cost_micros") or c.endswith("average_cpc") or c.endswith("cost_per_conversion")]:
            df[col.replace("_micros", "").replace("cost_per_conversion", "coste_por_conversion").replace("average_cpc", "cpc_medio").replace("cost", "coste")] = pd.to_numeric(df[col], errors="coerce") / 1_000_000
        campo = next((c for c in df.columns if c.endswith("campaign.name")), None)
        df["marca"] = df[campo].map(marca_de) if campo else "otros"
        for m, g in df.groupby("marca"):
            carpeta = os.path.join(OUT, m); os.makedirs(carpeta, exist_ok=True)
            ruta = os.path.join(carpeta, f"ads_{m}_{nombre}_{desde}_{hasta}.csv")
            g.drop(columns=["marca"]).to_csv(ruta, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
            print(f"{m}={len(g):,}", end=" ")
        print()
    print(f"Listo. Archivos en {OUT}")


if __name__ == "__main__":
    main()
