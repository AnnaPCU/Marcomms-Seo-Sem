#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gsc_recon.py — FASE 1: reconocimiento, sin guardar datos.

1. Renueva el token (nunca abre navegador: si el refresh falla, corta y avisa).
2. Lista propiedades y las compara con las 10 de CLAUDE.md §4.
3. Por propiedad: serie diaria completa (dimensión date) desde antes de los 16
   meses -> primera y última fecha con datos reales, días con datos.
4. Muestra de los últimos 28 días finales de cada uno de los 4 cortes para
   estimar filas. La muestra se cuenta y se descarta, no se escribe a disco.

Log de cada llamada en scripts/log_recon_<fecha>.jsonl
"""
import json, math, os, sys, time, datetime as dt

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
HOY = dt.date.today()
LOG = os.path.join(HERE, f"log_recon_{HOY:%Y%m%d}.jsonl")

PROPIEDADES = {
    "cu": [("https://espana.controlunion.com/", "España"),
           ("https://portugal.controlunion.com/", "Portugal"),
           ("https://northamerica.controlunion.com/", "Norteamérica"),
           ("https://argentina.controlunion.com/", "Argentina"),
           ("https://brasil.controlunion.com/", "Brasil"),
           ("https://mexico.controlunion.com/", "México"),
           ("https://chile.controlunion.com/", "Chile"),
           ("https://peru.controlunion.com/", "Perú")],
    "ps": [("https://americas.peterson-solutions.com/", "Américas"),
           ("https://iberia.peterson-solutions.com/", "Iberia")],
}
CORTES = {"queries": ["query", "country", "date"],
          "pages": ["page", "date"],
          "query_page": ["query", "page"],
          "devices": ["query", "device"]}
ROW_LIMIT = 25000
PAUSA = 0.3
MUESTRA_DIAS = 28


def log(**kw):
    kw["ts"] = dt.datetime.now().isoformat(timespec="seconds")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(kw, ensure_ascii=False) + "\n")


def autenticar():
    tok = os.path.join(ROOT, "token.json")
    creds = Credentials.from_authorized_user_file(tok, SCOPES)
    if not creds.valid:
        if not (creds.expired and creds.refresh_token):
            sys.exit("TOKEN: sin refresh_token. Hay que reautorizar (gsc_export.py --reset).")
        try:
            creds.refresh(Request())
        except Exception as e:
            sys.exit(f"TOKEN VENCIDO: el refresh falló ({type(e).__name__}: {e}).\n"
                     "Hay que reautorizar con tmisrahi@onepeterson.com.")
        with open(tok, "w") as f:
            f.write(creds.to_json())
        print(f"Token renovado. Nuevo vencimiento del access token: {creds.expiry}Z")
    else:
        print(f"Token vigente hasta {creds.expiry}Z")
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def query(svc, site, inicio, fin, dims, paginar=True):
    """Devuelve (filas, estado). Loguea cada llamada."""
    filas, start = [], 0
    while True:
        body = {"startDate": str(inicio), "endDate": str(fin), "dimensions": dims,
                "type": "web", "dataState": "final",
                "rowLimit": ROW_LIMIT, "startRow": start}
        try:
            r = svc.searchanalytics().query(siteUrl=site, body=body).execute()
            lote = r.get("rows", [])
            log(fase="recon", site=site, body=body, status=200, rows=len(lote))
        except HttpError as e:
            st = e.resp.status if e.resp else None
            log(fase="recon", site=site, body=body, status=st, error=str(e)[:300])
            return filas, f"HTTP {st}"
        filas.extend(lote)
        if len(lote) < ROW_LIMIT or not paginar:
            break
        start += ROW_LIMIT
        time.sleep(PAUSA)
    time.sleep(PAUSA)
    return filas, "ok"


def main():
    svc = autenticar()
    open(LOG, "a").close()

    # --- 2. propiedades ------------------------------------------------------
    sitios = svc.sites().list().execute().get("siteEntry", [])
    log(fase="recon", call="sites.list", rows=len(sitios))
    vistos = {s["siteUrl"]: s["permissionLevel"] for s in sitios}
    conocidas = {u: (m, n) for m, v in PROPIEDADES.items() for u, n in v}
    print(f"\n{len(sitios)} propiedades visibles con esta cuenta:")
    for u in sorted(vistos):
        if u in conocidas:
            tag = f"<- {conocidas[u][0].upper()} {conocidas[u][1]}"
        else:
            tag = "   (NO está en CLAUDE.md §4)"
        print(f"  {vistos[u]:<22} {u:<48} {tag}")
    faltan = [u for u in conocidas if u not in vistos]
    if faltan:
        print("\n[!] En CLAUDE.md pero NO visibles:")
        for u in faltan:
            print("    " + u)

    # --- 3 y 4. cobertura + muestras ----------------------------------------
    inicio_sonda = dt.date(2025, 4, 1)          # bien antes de los 16 meses
    limite_16m = HOY - dt.timedelta(days=int(16 * 30.4375))
    print(f"\nHoy {HOY}. 16 meses atrás ~ {limite_16m}. Sondeo desde {inicio_sonda}.\n")

    # baseline: exponente de crecimiento de claves únicas (42 d -> 363 d)
    base = {}
    for m in ("cu", "ps"):
        a = pd.read_csv(os.path.join(ROOT, "datos/gsc", f"gsc_{m}_ads_queries.csv"))
        b = pd.read_csv(os.path.join(ROOT, "datos/gsc", f"gsc_{m}_12m_queries.csv"))
        for prop in b["property"].unique():
            na, nb = (a["property"] == prop).sum(), (b["property"] == prop).sum()
            if na > 0 and nb > 0:
                base[prop] = math.log(nb / na) / math.log(363 / 42)

    resumen, series = [], {}
    for marca, props in PROPIEDADES.items():
        for site, nombre in props:
            if site not in vistos:
                resumen.append(dict(marca=marca.upper(), propiedad=nombre, nota="no visible"))
                continue
            filas, st = query(svc, site, inicio_sonda, HOY, ["date"])
            if st != "ok":
                print(f"  {nombre}: serie diaria falló ({st}); reintento desde {limite_16m}")
                filas, st = query(svc, site, limite_16m, HOY, ["date"])
            fechas = sorted(r["keys"][0] for r in filas)
            if not fechas:
                resumen.append(dict(marca=marca.upper(), propiedad=nombre, nota=f"sin datos ({st})"))
                print(f"  {nombre:<13} sin datos ({st})")
                continue
            d0, d1 = dt.date.fromisoformat(fechas[0]), dt.date.fromisoformat(fechas[-1])
            span = (d1 - d0).days + 1
            imp_tot = sum(r["impressions"] for r in filas)
            clk_tot = sum(r["clicks"] for r in filas)
            series[nombre] = pd.DataFrame(
                [{"date": r["keys"][0], "clicks": r["clicks"], "impressions": r["impressions"]}
                 for r in filas])
            fila = dict(marca=marca.upper(), propiedad=nombre, primera=str(d0), ultima=str(d1),
                        dias_span=span, dias_con_datos=len(fechas),
                        impresiones=imp_tot, clics=clk_tot,
                        exp_unicas=round(base.get(nombre, 0.75), 2))
            # muestras de 28 días finales
            m1 = d1
            m0 = d1 - dt.timedelta(days=MUESTRA_DIAS - 1)
            for corte, dims in CORTES.items():
                f_m, st_m = query(svc, site, m0, m1, dims)
                n = len(f_m)
                if "date" in dims:
                    est = n * span / MUESTRA_DIAS
                else:
                    est = n * (span / MUESTRA_DIAS) ** base.get(nombre, 0.75)
                fila[f"m28_{corte}"] = n
                fila[f"est_{corte}"] = int(round(est))
                if st_m != "ok":
                    fila["nota"] = (fila.get("nota", "") + f" {corte}:{st_m}").strip()
            resumen.append(fila)
            muestras = " ".join(f"{c}={fila['m28_' + c]}" for c in CORTES)
            print(f"  {marca.upper()} {nombre:<13} {d0} -> {d1}  ({span} d, {len(fechas)} con datos, "
                  f"{imp_tot:,} impr.)  muestra28: {muestras}")

    df = pd.DataFrame(resumen)
    out = os.path.join(HERE, f"recon_{HOY:%Y%m%d}.csv")
    df.to_csv(out, index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    print("\n" + df.to_string(index=False))
    print(f"\nResumen -> {out}\nLog     -> {LOG}")
    # serie mensual por propiedad (para ver dónde arranca realmente)
    for n, s in series.items():
        s["mes"] = s["date"].str[:7]
        g = s.groupby("mes")[["impressions", "clicks"]].sum()
        g["dias"] = s.groupby("mes")["date"].count()
        print(f"\n{n}: por mes\n" + g.to_string())


if __name__ == "__main__":
    main()
