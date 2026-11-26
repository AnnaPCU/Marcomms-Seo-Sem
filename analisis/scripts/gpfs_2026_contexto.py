# -*- coding: utf-8 -*-
"""
gpfs_2026_contexto.py — foto de solo lectura de la cuenta de Google Ads para el informe GPFS 2026:
configuración de conversiones, conversiones que dispararon (ago–sep 2026), totales de la cuenta, cuota de impresiones
de las campañas de EE.UU. (sep 2026), segmentación geográfica y listas de negativas compartidas.
Sale a datos/ads/api/gpfs_contexto_<AAAAMMDD>.json
"""
import datetime as dt, json, os, re
from google.ads.googleads.client import GoogleAdsClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
client = GoogleAdsClient.load_from_storage(os.path.join(ROOT, "google-ads.yaml"))
cid = json.load(open(os.path.join(ROOT, "google-ads.cuentas.json")))["cuentas"]["principal"]
svc = client.get_service("GoogleAdsService")


def q(g):
    return [r for b in svc.search_stream(customer_id=cid, query=g) for r in b.results]


out = {"fecha": str(dt.date.today())}
c = q("SELECT customer.currency_code, customer.time_zone, customer.auto_tagging_enabled, customer.conversion_tracking_setting.conversion_tracking_id FROM customer")[0].customer
out["cuenta"] = dict(moneda=c.currency_code, zona=c.time_zone, autotag=c.auto_tagging_enabled, tag=f"AW-{c.conversion_tracking_setting.conversion_tracking_id}")
out["acciones"] = [dict(nombre=r.conversion_action.name, tipo=r.conversion_action.type_.name, categoria=r.conversion_action.category.name,
                        primaria=r.conversion_action.primary_for_goal, cuenta=r.conversion_action.counting_type.name)
                   for r in q("SELECT conversion_action.name, conversion_action.type, conversion_action.category, conversion_action.primary_for_goal, conversion_action.counting_type FROM conversion_action WHERE conversion_action.status = 'ENABLED'")]
disp = {}
for r in q("SELECT segments.conversion_action_name, metrics.all_conversions, metrics.conversions FROM campaign WHERE segments.date BETWEEN '2026-08-01' AND '2026-09-30' AND metrics.all_conversions > 0"):
    d = disp.setdefault(r.segments.conversion_action_name, [0, 0]); d[0] += r.metrics.all_conversions; d[1] += r.metrics.conversions
out["disparos_ago_sep"] = {k: dict(todas=round(v[0]), conversiones=round(v[1])) for k, v in disp.items()}
m = q("SELECT metrics.clicks, metrics.cost_micros, metrics.impressions FROM customer WHERE segments.date BETWEEN '2026-08-01' AND '2026-09-30'")[0].metrics
out["cuenta_ago_sep"] = dict(clics=m.clicks, coste=round(m.cost_micros / 1e6), impresiones=m.impressions)
out["usa_sep"] = [dict(campana=r.campaign.name, clics=r.metrics.clicks, coste=round(r.metrics.cost_micros / 1e6), cuota=round(r.metrics.search_impression_share, 2),
                       cuota_arriba=round(r.metrics.search_top_impression_share, 2), perdida_ranking=round(r.metrics.search_rank_lost_impression_share, 2),
                       perdida_presupuesto=round(r.metrics.search_budget_lost_impression_share, 2))
                  for r in q("SELECT campaign.name, metrics.clicks, metrics.cost_micros, metrics.search_impression_share, metrics.search_top_impression_share, metrics.search_rank_lost_impression_share, metrics.search_budget_lost_impression_share FROM campaign WHERE segments.date BETWEEN '2026-09-01' AND '2026-09-30' AND campaign.name LIKE 'CU United States%'")]
out["geo_usa"] = {r.campaign.name: r.campaign.geo_target_type_setting.positive_geo_target_type.name
                  for r in q("SELECT campaign.name, campaign.geo_target_type_setting.positive_geo_target_type FROM campaign WHERE campaign.status = 'ENABLED' AND campaign.name LIKE 'CU United States%'")}
out["listas_negativas"] = [r.shared_set.name for r in q("SELECT shared_set.name FROM shared_set WHERE shared_set.status = 'ENABLED' AND shared_set.type = 'NEGATIVE_KEYWORDS'")]
ruta = os.path.join(ROOT, "datos", "ads", "api", f"gpfs_contexto_{dt.date.today():%Y%m%d}.json")
json.dump(out, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("->", ruta)
print(json.dumps(out, ensure_ascii=False, indent=1)[:2500])
