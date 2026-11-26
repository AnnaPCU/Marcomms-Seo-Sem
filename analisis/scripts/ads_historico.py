# -*- coding: utf-8 -*-
"""
ads_historico.py — gasto, clics, impresiones y conversiones por mes calendario, por campaña y por grupo de anuncios,
desde la API de Google Ads (solo lectura), para el filtro de meses anteriores y la vista «Histórico» del tablero.

Junta dos cuentas:
  · la actual, «Control Union - (en ARG)» (google-ads.cuentas.json → cuentas.principal), en pesos, desde jul 2026;
  · la anterior, «Peterson Technologies» (→ historicas), en euros: tiene las campañas CU y PS de feb a jul 2026.
    Growr y las campañas sin prefijo de marca no entran (marca_de las deja en «otros»).
Los euros se pasan a pesos con el promedio del mes del tipo de cambio oficial del BCRA (Comunicación A 3500,
API de estadísticas cambiarias). Cada fila guarda la moneda original, el importe original y el tipo de cambio usado.
Incluye campañas y grupos que hoy están pausados o eliminados: el histórico tiene que sumar todo lo que se gastó.

Uso:
  python ads_historico.py                          desde 2024-01 hasta ayer (el mes en curso queda parcial)
  python ads_historico.py --desde 2026-01-01 --hasta 2026-09-30

Salida: informe/datos_ads_historico.json (lo carga scripts/publicar.py --solo historico del tablero)
        informe/tipo_cambio_eur_ars.json   promedio mensual usado, con la fuente
        datos/ads/api/<marca>/ads_<marca>_historico_<desde>_<hasta>.csv   archivo por marca (nunca uno común)
Solo campañas de Search (las mismas que la vista de presupuesto).
"""
import argparse, calendar, datetime as dt, json, os
import pandas as pd
import requests
import yaml
from google.ads.googleads.client import GoogleAdsClient
from ads_export import YAML, CUENTAS, marca_de, consultar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = os.path.join(ROOT, "datos", "ads", "api")
INF = os.path.join(ROOT, "informe")
HOY = dt.date.today()
BCRA = "https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Cotizaciones/{moneda}"

METRICAS = "metrics.cost_micros, metrics.clicks, metrics.impressions, metrics.conversions"
GAQL_CAMP = f"""SELECT customer.currency_code, campaign.id, campaign.name, campaign.status, segments.month, {METRICAS}
FROM campaign WHERE segments.date BETWEEN '{{a}}' AND '{{b}}' AND campaign.advertising_channel_type = 'SEARCH'"""
GAQL_GRUPO = f"""SELECT campaign.id, campaign.name, ad_group.id, ad_group.name, ad_group.status, segments.month, {METRICAS}
FROM ad_group WHERE segments.date BETWEEN '{{a}}' AND '{{b}}' AND campaign.advertising_channel_type = 'SEARCH'"""


def cliente(login=None):
    cfg = yaml.safe_load(open(YAML, encoding="utf-8"))
    if login:
        cfg["login_customer_id"] = str(login)
    return GoogleAdsClient.load_from_dict(cfg)


def a_df(filas, extra):
    if not filas:
        return pd.DataFrame()
    df = pd.DataFrame(filas)
    out = pd.DataFrame({k: df[v].astype(str) for k, v in extra.items()})
    out["mes"] = df["segments.month"].str[:7]
    out["coste"] = pd.to_numeric(df.get("metrics.cost_micros", 0)).fillna(0) / 1e6
    out["clics"] = pd.to_numeric(df.get("metrics.clicks", 0)).fillna(0).astype(int)
    out["impresiones"] = pd.to_numeric(df.get("metrics.impressions", 0)).fillna(0).astype(int)
    out["conversiones"] = pd.to_numeric(df.get("metrics.conversions", 0)).fillna(0)
    out["marca"] = out["campana"].map(marca_de)
    return out[(out["marca"] != "otros") & ((out["coste"] > 0) | (out["clics"] > 0) | (out["impresiones"] > 0))]


def tipo_cambio(moneda, meses):
    """Promedio mensual del tipo de cambio oficial BCRA (pesos por unidad de `moneda`) para cada mes pedido."""
    out = {}
    for mes in sorted(meses):
        y, m = map(int, mes.split("-"))
        fin = min(dt.date(y, m, calendar.monthrange(y, m)[1]), HOY)
        r = requests.get(BCRA.format(moneda=moneda), params={"fechadesde": f"{mes}-01", "fechahasta": str(fin)}, timeout=60)
        r.raise_for_status()
        vals = [d["tipoCotizacion"] for f in r.json()["results"] for d in f["detalle"] if d["codigoMoneda"] == moneda]
        if not vals:
            raise SystemExit(f"El BCRA no devolvió cotizaciones de {moneda} para {mes}.")
        out[mes] = dict(promedio=round(sum(vals) / len(vals), 4), dias=len(vals))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde"); ap.add_argument("--hasta")
    a = ap.parse_args()
    hasta = dt.date.fromisoformat(a.hasta) if a.hasta else HOY - dt.timedelta(days=1)
    desde = dt.date.fromisoformat(a.desde) if a.desde else dt.date(2024, 1, 1)
    logp = os.path.join(API, f"log_ads_{HOY:%Y%m%d}.jsonl")

    cuentas = [dict(id=CUENTAS["cuentas"]["principal"], login=None, cuenta="actual", nombre="Control Union - (en ARG)")] + CUENTAS.get("historicas", [])
    campos, grupos = [], []
    for c in cuentas:
        def log(**kw):
            kw.update(reporte="historico", cuenta=c["id"], desde=str(desde), hasta=str(hasta), ts=dt.datetime.now().isoformat(timespec="seconds"))
            open(logp, "a", encoding="utf-8").write(json.dumps(kw, ensure_ascii=False) + "\n")
        cli = cliente(c.get("login"))
        crudo = consultar(cli, c["id"], GAQL_CAMP.format(a=desde, b=hasta), log)
        moneda = crudo[0]["customer.currency_code"] if crudo else "ARS"
        df = a_df(crudo, {"ads_id": "campaign.id", "campana": "campaign.name", "estado": "campaign.status"})
        dg = a_df(consultar(cli, c["id"], GAQL_GRUPO.format(a=desde, b=hasta), log),
                  {"campana_ads_id": "campaign.id", "campana": "campaign.name", "ads_id": "ad_group.id", "grupo": "ad_group.name", "estado": "ad_group.status"})
        for x in (df, dg):
            if not x.empty:
                x["cuenta"], x["moneda"] = c["cuenta"], moneda
        campos.append(df); grupos.append(dg)
        print(f"{c['nombre']} ({c['id']}, {moneda}): {len(df)} campaña-mes, {len(dg)} grupo-mes")
    camp = pd.concat([d for d in campos if not d.empty], ignore_index=True)
    grup = pd.concat([d for d in grupos if not d.empty], ignore_index=True)
    if camp.empty:
        raise SystemExit("La API no devolvió filas.")

    # tipo de cambio: pesos por unidad de la moneda de la cuenta, promedio del mes
    tc = {}
    for moneda in set(camp["moneda"]) - {"ARS"}:
        tc[moneda] = tipo_cambio(moneda, set(camp.loc[camp["moneda"] == moneda, "mes"]))
    json.dump(dict(fuente="BCRA, API de estadísticas cambiarias (tipo de cambio de referencia, promedio de los días hábiles del mes)",
                   generado=dt.datetime.now().isoformat(timespec="seconds"), tipos=tc),
              open(os.path.join(INF, "tipo_cambio_eur_ars.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    factor = lambda moneda, mes: 1.0 if moneda == "ARS" else tc[moneda][mes]["promedio"]
    for x in (camp, grup):
        x["tipo_cambio"] = [factor(m, mes) for m, mes in zip(x["moneda"], x["mes"])]
        x["coste_original"] = x["coste"]
        x["coste"] = x["coste"] * x["tipo_cambio"]

    for m, g in camp.groupby("marca"):
        os.makedirs(os.path.join(API, m), exist_ok=True)
        g.drop(columns="marca").to_csv(os.path.join(API, m, f"ads_{m}_historico_{desde}_{hasta}.csv"), index=False, encoding="utf-8-sig")

    def rango(mes):
        y, mm = map(int, mes.split("-"))
        ini, fin = max(dt.date(y, mm, 1), desde), min(dt.date(y, mm, calendar.monthrange(y, mm)[1]), hasta)
        return dict(desde=str(ini), hasta=str(fin), dias=(fin - ini).days + 1)

    def num(r):
        d = dict(coste=round(float(r.coste), 2), clics=int(r.clics), impresiones=int(r.impresiones), conversiones=round(float(r.conversiones), 2))
        if r.moneda != "ARS":
            d.update(moneda_original=r.moneda, coste_original=round(float(r.coste_original), 2), tipo_cambio=r.tipo_cambio)
        return d

    salida = dict(
        desde=str(desde), hasta=str(hasta), generado=dt.datetime.now().isoformat(timespec="seconds"),
        campanas=[dict(ads_id=r.ads_id, campana=r.campana, marca=r.marca.upper(), estado=r.estado, cuenta=r.cuenta, mes=r.mes, **rango(r.mes), **num(r))
                  for r in camp.sort_values(["mes", "campana"]).itertuples()],
        grupos=[dict(campana_ads_id=r.campana_ads_id, campana=r.campana, ads_id=r.ads_id, grupo=r.grupo, estado=r.estado, mes=r.mes, **num(r))
                for r in grup.sort_values(["mes", "campana", "grupo"]).itertuples()],
    )
    json.dump(salida, open(os.path.join(INF, "datos_ads_historico.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    meses = camp.groupby(["mes", "cuenta"]).agg(campanas=("ads_id", "nunique"), coste_ars=("coste", "sum"), clics=("clics", "sum"))
    print(meses.to_string(float_format=lambda x: f"{x:,.0f}"))
    print("tipo de cambio:", {m: {k: v["promedio"] for k, v in t.items()} for m, t in tc.items()})
    print(f"{len(camp)} campaña-mes, {len(grup)} grupo-mes, {camp['ads_id'].nunique()} campañas -> informe/datos_ads_historico.json")


if __name__ == "__main__":
    main()
