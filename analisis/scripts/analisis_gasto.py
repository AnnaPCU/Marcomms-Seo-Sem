# -*- coding: utf-8 -*-
"""
analisis_gasto.py — gasto por cliente, país, campaña y grupo de anuncios para una ventana ya extraída por API.

Lee datos/ads/api/{cu,pcu,ps}/ads_<marca>_anuncios_<desde>_<hasta>.csv (rendimiento por anuncio: suma el gasto
completo de cada grupo, incluido el tramo que Google esconde en «otros términos de búsqueda»; el reporte de términos
solo muestra la mitad del gasto). Suma coste, clics y conversiones por campaña y grupo. Escribe:
  informe/datos_gasto_<desde>_<hasta>.json   (la ventana pedida)
  informe/datos_gasto_actual.json            (copia: la última corrida, la que leen la vista y el tablero)

Uso: python analisis_gasto.py --desde 2026-09-01 --hasta 2026-09-27
     (sin argumentos toma la ventana más reciente que exista en datos/ads/api/cu)
"""
import argparse, glob, json, os, re, shutil
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = os.path.join(ROOT, "datos", "ads", "api")
INF = os.path.join(ROOT, "informe")
MARCAS = {"cu": "Control Union", "pcu": "ISO 27001 (PCU)", "ps": "Peterson Solutions"}


def unidad(nombre):
    """País de la campaña por palabra clave, en cualquier parte del nombre: los prefijos cambian seguido
    («PCU Argentina» → «PCU Tech» → «PCU - Argentina»). «Tech» es la unidad ISO 27001 de Argentina."""
    # naming estándar del equipo (skill paid-media-pcu): MARCA_PAÍS_TIPO_NORMA_IDIOMA, p. ej. CU_US_SEARCH_GPFS-2026_EN
    m = re.match(r"^(?:CUC|CU|PS|PCU)_([A-Z]{2})_", nombre)
    if m:
        return {"US": "CUC USA", "CA": "Canadá", "MX": "México", "AR": "Argentina", "ES": "España", "PT": "Portugal",
                "BR": "Brasil", "CL": "Chile", "PE": "Perú"}.get(m.group(1), "Sin asignar")
    for clave, u in [("España", "España"), ("Portugal", "Portugal"), ("Canada", "Canadá"), ("CUC USA", "CUC USA"), ("United States", "CUC USA"),
                     ("Argentina", "Argentina"), ("PCU Tech", "Argentina")]:
        if clave in nombre:
            return u
    return "Sin asignar"


ap = argparse.ArgumentParser()
ap.add_argument("--desde")
ap.add_argument("--hasta")
a = ap.parse_args()
if not (a.desde and a.hasta):
    ventanas = sorted(re.search(r"anuncios_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})", f).groups() for f in glob.glob(os.path.join(API, "cu", "ads_cu_anuncios_*.csv")))
    a.desde, a.hasta = max(ventanas, key=lambda v: v[1])
dias = (pd.Timestamp(a.hasta) - pd.Timestamp(a.desde)).days + 1

# presupuesto diario establecido en Google Ads, del snapshot de estructura más reciente (por id de campaña)
snaps = sorted(glob.glob(os.path.join(API, "estructura_*")))
PRESUPUESTO, ESTADO = {}, {}
if snaps:
    est = pd.read_csv(os.path.join(snaps[-1], "campanas.csv"), encoding="utf-8-sig")
    for _, r in est.iterrows():
        m = pd.to_numeric(r.get("campaign_budget.amount_micros"), errors="coerce")
        ESTADO[str(r["campaign.id"])] = str(r["campaign.status"])
        # solo cuenta el presupuesto de campañas activas: una pausada o eliminada no puede gastarlo
        PRESUPUESTO[str(r["campaign.id"])] = None if pd.isna(m) or str(r["campaign.status"]) != "ENABLED" else round(float(m) / 1e6, 2)

filas = []
for marca, nombre in MARCAS.items():
    ruta = os.path.join(API, marca, f"ads_{marca}_anuncios_{a.desde}_{a.hasta}.csv")
    if not os.path.exists(ruta):
        print(f"  sin archivo para {marca}: {os.path.basename(ruta)}")
        continue
    d = pd.read_csv(ruta, encoding="utf-8-sig")
    for c in ("metrics.coste", "metrics.clicks", "metrics.conversions", "metrics.impressions"):
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
    d["campaign.id"] = d["campaign.resource_name"].astype(str).str.rsplit("/", n=1).str[-1]
    g = d.groupby(["campaign.id", "campaign.name", "ad_group.name"], as_index=False)[["metrics.coste", "metrics.clicks", "metrics.conversions", "metrics.impressions"]].sum()
    for _, r in g.iterrows():
        filas.append(dict(marca=nombre, unidad=unidad(r["campaign.name"]), campana=r["campaign.name"], campana_id=str(r["campaign.id"]),
                          presupuesto_dia=PRESUPUESTO.get(str(r["campaign.id"])), campana_estado=ESTADO.get(str(r["campaign.id"]), ""), grupo=r["ad_group.name"],
                          coste=round(float(r["metrics.coste"]), 2), clics=int(r["metrics.clicks"]), conv=float(r["metrics.conversions"]),
                          impresiones=int(r["metrics.impressions"])))
filas.sort(key=lambda f: -f["coste"])
salida = dict(ventana=f"{a.desde}_{a.hasta}", desde=a.desde, hasta=a.hasta, dias=dias, snapshot=os.path.basename(snaps[-1]) if snaps else None, filas=filas)
ruta = os.path.join(INF, f"datos_gasto_{a.desde}_{a.hasta}.json")
json.dump(salida, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
shutil.copyfile(ruta, os.path.join(INF, "datos_gasto_actual.json"))
tot = sum(f["coste"] for f in filas)
print(f"-> {os.path.basename(ruta)} y datos_gasto_actual.json: {len(filas)} filas, {dias} días, ARS {tot:,.0f} (ARS {tot/dias:,.0f}/día)")
