#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gsc_historico.py — FASE 2: extracción del histórico máximo de Search Console.

Por marca (nunca un archivo común), por propiedad, cinco cortes:
  queries     query + country + date   (mes a mes, paginado)
  pages       page + date              (mes a mes, paginado)
  query_page  query + page             (ventana completa, paginado)
  devices     query + device           (ventana completa, paginado)
  daily       date                     (ventana completa; totales por propiedad)

Salida: datos/gsc-historico/<marca>/gsc_<marca>_hist_<corte>.csv
Log:    datos/gsc-historico/<marca>/log_extraccion_<fecha>.jsonl  (una línea por llamada)

Parámetros API: type=web, dataState=final, rowLimit=25000, paginación por startRow.
Ventana de sondeo: 2025-04-01 → hoy. Google solo devuelve lo que retiene.
"""
import json, os, sys, time, datetime as dt

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "datos", "gsc-historico")
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
HOY = dt.date.today()
INICIO = dt.date(2025, 4, 1)
ROW_LIMIT = 25000
PAUSA = 0.25

PROPIEDADES = {
    "cu": [("https://espana.controlunion.com/", "España", True),
           ("https://portugal.controlunion.com/", "Portugal", True),
           ("https://northamerica.controlunion.com/", "Norteamérica", True),
           ("https://argentina.controlunion.com/", "Argentina", True),
           ("https://brasil.controlunion.com/", "Brasil", False),
           ("https://mexico.controlunion.com/", "México", False),
           ("https://chile.controlunion.com/", "Chile", False),
           ("https://peru.controlunion.com/", "Perú", False)],
    "ps": [("https://americas.peterson-solutions.com/", "Américas", True),
           ("https://iberia.peterson-solutions.com/", "Iberia", False)],
}
NOMBRE = {"cu": "CONTROL UNION", "ps": "PETERSON SOLUTIONS"}

# (corte, dimensiones, por_mes)
CORTES = [("queries", ["query", "country", "date"], True),
          ("pages", ["page", "date"], True),
          ("query_page", ["query", "page"], False),
          ("devices", ["query", "device"], False),
          ("daily", ["date"], False)]


def autenticar():
    tok = os.path.join(ROOT, "token.json")
    creds = Credentials.from_authorized_user_file(tok, SCOPES)
    if not creds.valid:
        if not (creds.expired and creds.refresh_token):
            sys.exit("TOKEN sin refresh_token: reautorizar.")
        try:
            creds.refresh(Request())
        except Exception as e:
            sys.exit(f"TOKEN VENCIDO, el refresh falló ({e}). Reautorizar con tmisrahi@onepeterson.com.")
        with open(tok, "w") as f:
            f.write(creds.to_json())
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def meses(desde, hasta):
    d = desde.replace(day=1)
    while d <= hasta:
        if d.month == 12:
            sig = d.replace(year=d.year + 1, month=1)
        else:
            sig = d.replace(month=d.month + 1)
        yield max(d, desde), min(sig - dt.timedelta(days=1), hasta)
        d = sig


class Extractor:
    def __init__(self, svc, log_path):
        self.svc, self.log_path = svc, log_path
        self.llamadas = 0

    def log(self, **kw):
        kw["ts"] = dt.datetime.now().isoformat(timespec="seconds")
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(kw, ensure_ascii=False) + "\n")

    def query(self, site, inicio, fin, dims, corte):
        filas, start = [], 0
        while True:
            body = {"startDate": str(inicio), "endDate": str(fin), "dimensions": dims,
                    "type": "web", "dataState": "final",
                    "rowLimit": ROW_LIMIT, "startRow": start}
            lote, intento = None, 0
            while lote is None:
                t0 = time.time()
                try:
                    r = self.svc.searchanalytics().query(siteUrl=site, body=body).execute()
                    lote = r.get("rows", [])
                    self.llamadas += 1
                    self.log(corte=corte, site=site, body=body, status=200,
                             rows=len(lote), ms=int((time.time() - t0) * 1000))
                except HttpError as e:
                    st = e.resp.status if e.resp else None
                    intento += 1
                    self.log(corte=corte, site=site, body=body, status=st,
                             error=str(e)[:300], intento=intento)
                    if st in (429, 500, 502, 503, 504) and intento < 4:
                        time.sleep(5 * intento)
                        continue
                    print(f"      ! HTTP {st} en {corte} {inicio}..{fin} startRow={start}: se abandona el tramo")
                    return filas, False
                except Exception as e:                      # timeout de red, conexión caída
                    intento += 1
                    self.log(corte=corte, site=site, body=body, status="red",
                             error=f"{type(e).__name__}: {str(e)[:200]}", intento=intento)
                    if intento < 6:
                        time.sleep(10 * intento)
                        continue
                    print(f"      ! red: {type(e).__name__} en {corte} {inicio}..{fin}: se abandona el tramo")
                    return filas, False
            for row in lote:
                d = dict(zip(dims, row["keys"]))
                d.update(clicks=row["clicks"], impressions=row["impressions"],
                         ctr=round(row["ctr"], 6), position=round(row["position"], 2))
                filas.append(d)
            if len(lote) < ROW_LIMIT:
                break
            start += ROW_LIMIT
            time.sleep(PAUSA)
        time.sleep(PAUSA)
        return filas, True


def extraer(svc, marca):
    props = PROPIEDADES[marca]
    carpeta = os.path.join(OUT, marca)
    os.makedirs(carpeta, exist_ok=True)
    ex = Extractor(svc, os.path.join(carpeta, f"log_extraccion_{HOY:%Y%m%d}.jsonl"))
    ex.log(evento="inicio", marca=marca, ventana=[str(INICIO), str(HOY)])
    print(f"\n{'=' * 66}\n{NOMBRE[marca]}  ·  {len(props)} propiedades  ·  {INICIO} → {HOY}\n{'=' * 66}")
    resumen = []
    for corte, dims, por_mes in CORTES:
        todo, ok_total = [], True
        print(f"\n  [{corte}] {'+'.join(dims)}" + ("  (mes a mes)" if por_mes else ""))
        for site, etiqueta, con_campana in props:
            filas_prop = []
            tramos = list(meses(INICIO, HOY)) if por_mes else [(INICIO, HOY)]
            for a, b in tramos:
                f, ok = ex.query(site, a, b, dims, corte)
                ok_total &= ok
                filas_prop.extend(f)
            for f in filas_prop:
                f["property"] = etiqueta
                f["site"] = site
                f["con_campana"] = "si" if con_campana else "no"
            print(f"      {etiqueta:<14} {len(filas_prop):>8,} filas".replace(",", "."))
            todo.extend(filas_prop)
            resumen.append(dict(marca=marca, corte=corte, propiedad=etiqueta, filas=len(filas_prop)))
        if not todo:
            print("      (sin datos)")
            continue
        df = pd.DataFrame(todo)
        df.insert(0, "brand", NOMBRE[marca])
        df.insert(1, "window", "hist")
        cols = (["brand", "window", "property", "site", "con_campana"] + dims +
                ["clicks", "impressions", "ctr", "position"])
        df = df[cols]
        orden = ["property"] + (["date"] if "date" in dims else []) + ["impressions"]
        df = df.sort_values(orden, ascending=[True] * (len(orden) - 1) + [False])
        ruta = os.path.join(carpeta, f"gsc_{marca}_hist_{corte}.csv")
        df.to_csv(ruta, index=False, encoding="utf-8-sig")
        ex.log(evento="archivo", corte=corte, ruta=ruta, filas=len(df), completo=ok_total)
        print(f"      -> {os.path.basename(ruta)}  ({len(df):,} filas{'' if ok_total else ', INCOMPLETO'})".replace(",", "."))
    ex.log(evento="fin", marca=marca, llamadas=ex.llamadas)
    print(f"\n  {ex.llamadas} llamadas a la API para {NOMBRE[marca]}")
    return resumen


def main():
    marcas = sys.argv[1:] or ["cu", "ps"]
    svc = autenticar()
    t0 = time.time()
    res = []
    for m in marcas:
        res.extend(extraer(svc, m))
    pd.DataFrame(res).to_csv(os.path.join(OUT, f"resumen_extraccion_{HOY:%Y%m%d}.csv"),
                             index=False, encoding="utf-8-sig")
    print(f"\nListo en {int(time.time() - t0)} s. Archivos en {OUT}")


if __name__ == "__main__":
    main()
