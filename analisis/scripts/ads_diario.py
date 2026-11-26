# -*- coding: utf-8 -*-
"""
ads_diario.py — gasto por campaña y por día desde la API de Google Ads (solo lectura), para la vista «Día a día» del tablero.

Uso:
  python ads_diario.py                          del 1 del mes anterior a ayer
  python ads_diario.py --desde 2026-09-01 --hasta 2026-10-01

Salida:
  datos/ads/api/<marca>/ads_<marca>_diario_<desde>_<hasta>.csv   archivo por marca (nunca uno común)
  informe/datos_gasto_diario.json                                 lo que carga scripts/publicar.py del tablero
Solo campañas de Search (las mismas que la vista de presupuesto). Google omite los días sin impresiones:
en el tablero, un día sin fila es un día sin gasto.
"""
import argparse, datetime as dt, json, os
import pandas as pd
from google.ads.googleads.client import GoogleAdsClient
from ads_export import YAML, CUENTAS, marca_de, consultar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = os.path.join(ROOT, "datos", "ads", "api")
INF = os.path.join(ROOT, "informe")
HOY = dt.date.today()

GAQL = """SELECT campaign.id, campaign.name, segments.date, metrics.cost_micros, metrics.clicks, metrics.impressions, metrics.conversions
FROM campaign WHERE segments.date BETWEEN '{a}' AND '{b}' AND campaign.advertising_channel_type = 'SEARCH'"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde"); ap.add_argument("--hasta")
    a = ap.parse_args()
    hasta = dt.date.fromisoformat(a.hasta) if a.hasta else HOY - dt.timedelta(days=1)
    desde = dt.date.fromisoformat(a.desde) if a.desde else (hasta.replace(day=1) - dt.timedelta(days=1)).replace(day=1)
    client = GoogleAdsClient.load_from_storage(YAML)
    logp = os.path.join(API, f"log_ads_{HOY:%Y%m%d}.jsonl")

    def log(**kw):
        kw.update(reporte="diario", desde=str(desde), hasta=str(hasta), ts=dt.datetime.now().isoformat(timespec="seconds"))
        open(logp, "a", encoding="utf-8").write(json.dumps(kw, ensure_ascii=False) + "\n")

    filas = consultar(client, CUENTAS["cuentas"]["principal"], GAQL.format(a=desde, b=hasta), log)
    if not filas:
        raise SystemExit("La API no devolvió filas.")
    df = pd.DataFrame(filas)
    df = pd.DataFrame({
        "ads_id": df["campaign.id"].astype(str), "campana": df["campaign.name"], "fecha": df["segments.date"],
        "coste": pd.to_numeric(df.get("metrics.cost_micros", 0)).fillna(0) / 1e6,
        "clics": pd.to_numeric(df.get("metrics.clicks", 0)).fillna(0).astype(int),
        "impresiones": pd.to_numeric(df.get("metrics.impressions", 0)).fillna(0).astype(int),
        "conversiones": pd.to_numeric(df.get("metrics.conversions", 0)).fillna(0),
    })
    df["marca"] = df["campana"].map(marca_de)
    for m, g in df[df["marca"] != "otros"].groupby("marca"):
        os.makedirs(os.path.join(API, m), exist_ok=True)
        g.drop(columns="marca").to_csv(os.path.join(API, m, f"ads_{m}_diario_{desde}_{hasta}.csv"), index=False, encoding="utf-8-sig")
    df = df[df["marca"] != "otros"].sort_values(["fecha", "campana"])
    salida = dict(desde=str(desde), hasta=str(hasta), generado=dt.datetime.now().isoformat(timespec="seconds"),
                  filas=[dict(ads_id=r.ads_id, campana=r.campana, fecha=r.fecha, coste=round(r.coste, 2), clics=int(r.clics),
                              impresiones=int(r.impresiones), conversiones=round(float(r.conversiones), 2)) for r in df.itertuples()])
    json.dump(salida, open(os.path.join(INF, "datos_gasto_diario.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(df)} filas ({df['ads_id'].nunique()} campañas, {df['fecha'].nunique()} días, ARS {df['coste'].sum():,.0f}) "
          f"{desde} → {hasta} -> informe/datos_gasto_diario.json")


if __name__ == "__main__":
    main()
