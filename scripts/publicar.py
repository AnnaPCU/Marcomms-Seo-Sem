# -*- coding: utf-8 -*-
"""
publicar.py — carga en Supabase lo que produce el proyecto de análisis (Optimizaciónes SEO-SEM/proyecto):
  1. campañas y grupos      ← datos/ads/api/estructura_<fecha>/{campanas,grupos}.csv (la más reciente)
  2. recomendaciones        ← informe/recomendaciones.json (lo genera scripts/exportar_recomendaciones.py)
  3. métricas por campaña   ← informe/datos_gasto_actual.json (mes en curso, del 1 al último día extraído; lo genera analisis_gasto.py)
  4. extracciones           ← fechas de los archivos de Search Console y Ads

Es idempotente: las recomendaciones que ya existen (misma clave) solo actualizan texto, evidencia y prioridad;
nunca el estado, el orden ni quién las movió. Las campañas y grupos se actualizan por nombre.

Variables de entorno (nunca en el repo):
  SUPABASE_URL          https://<ref>.supabase.co
  SUPABASE_SERVICE_KEY  service role key (Project Settings → API). Solo se usa desde esta máquina.
  PROYECTO_DIR          opcional; por defecto ../Optimizaciónes SEO-SEM/proyecto relativo a este repo.
Uso: python scripts/publicar.py [--solo campanas|recomendaciones|metricas|extracciones]
"""
import glob, json, os, re, sys
from datetime import datetime, timezone
import pandas as pd
import requests

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROY = os.environ.get("PROYECTO_DIR") or os.path.join(os.path.dirname(REPO), "Optimizaciónes SEO-SEM", "proyecto")
URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
if not URL or not KEY:
    sys.exit("Faltan SUPABASE_URL y SUPABASE_SERVICE_KEY en el entorno.")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
SOLO = sys.argv[sys.argv.index("--solo") + 1] if "--solo" in sys.argv else None


def api(metodo, tabla, params=None, cuerpo=None, prefer=None):
    h = dict(H)
    if prefer:
        h["Prefer"] = prefer
    r = requests.request(metodo, f"{URL}/rest/v1/{tabla}", headers=h, params=params, json=cuerpo, timeout=60)
    if r.status_code >= 300:
        sys.exit(f"{metodo} {tabla}: {r.status_code} {r.text[:400]}")
    return r.json() if r.text else None


def upsert(tabla, filas, conflicto):
    if not filas:
        return []
    return api("POST", tabla, params={"on_conflict": conflicto}, cuerpo=filas, prefer="resolution=merge-duplicates,return=representation")


def unidad_de(nombre):
    for pref, u in [("CU España", "España"), ("CU Portugal", "Portugal"), ("CU Canada", "Canadá"), ("CU United States", "Estados Unidos"),
                    ("CU Argentina", "Argentina"), ("PCU España", "España"), ("PCU Argentina", "Argentina"), ("PCU Tech", "Argentina"),
                    ("PS Argentina", "Argentina")]:
        if nombre.startswith(pref):
            return u
    return "Sin asignar"


def col(df, *sufijos):
    for s in sufijos:
        for c in df.columns:
            if c == s or c.endswith("." + s) or c.endswith(s):
                return c
    raise KeyError(sufijos)


# ------------------------------------------------------------------ 1. campañas y grupos
snaps = sorted(glob.glob(os.path.join(PROY, "datos", "ads", "api", "estructura_*")))
if not snaps:
    sys.exit("No hay datos/ads/api/estructura_* en el proyecto.")
snap = snaps[-1]
camp = pd.read_csv(os.path.join(snap, "campanas.csv"), encoding="utf-8-sig")
filas = []
for _, r in camp.iterrows():
    nombre = str(r["campaign.name"])
    micros = pd.to_numeric(r.get("campaign_budget.amount_micros"), errors="coerce")
    filas.append(dict(ads_id=str(r["campaign.id"]), nombre=nombre, marca=str(r["marca"]).upper(), unidad=unidad_de(nombre),
                      estado=str(r["campaign.status"]), presupuesto_dia=None if pd.isna(micros) else round(float(micros) / 1e6, 2)))
if SOLO in (None, "campanas"):
    upsert("campanas", filas, "nombre")
    print(f"campañas: {len(filas)} (snapshot {os.path.basename(snap)})")
CAMP = {c["nombre"]: c["id"] for c in api("GET", "campanas", params={"select": "id,nombre"})}

gru = pd.read_csv(os.path.join(snap, "grupos.csv"), encoding="utf-8-sig")
c_camp, c_nom, c_id, c_est = col(gru, "campaign.name"), col(gru, "ad_group.name"), col(gru, "ad_group.id"), col(gru, "ad_group.status")
filas = [dict(campana_id=CAMP[str(r[c_camp])], ads_id=str(r[c_id]), nombre=str(r[c_nom]), estado=str(r[c_est])) for _, r in gru.iterrows() if str(r[c_camp]) in CAMP]
if SOLO in (None, "campanas"):
    upsert("grupos", filas, "campana_id,nombre")
    print(f"grupos: {len(filas)}")
GRU = {(g["campana_id"], g["nombre"]): g["id"] for g in api("GET", "grupos", params={"select": "id,campana_id,nombre"})}


def campana_id(nombre):
    if not nombre:
        return None
    if nombre in CAMP:
        return CAMP[nombre]
    return next((v for k, v in CAMP.items() if k.startswith(nombre)), None)


# ------------------------------------------------------------------ 2. recomendaciones
if SOLO in (None, "recomendaciones"):
    ruta = os.path.join(PROY, "informe", "recomendaciones.json")
    recs = json.load(open(ruta, encoding="utf-8"))
    existentes = {r["clave"] for r in api("GET", "recomendaciones", params={"select": "clave"})}
    nuevas, viejas = [], []
    for r in recs:
        cid = campana_id(r.get("campana"))
        gid = GRU.get((cid, r["grupo"])) if cid and r.get("grupo") else None
        base = dict(clave=r["clave"], marca=r["marca"], tipo=r["tipo"], campana_id=cid, grupo_id=gid, sitio=r.get("sitio"), pagina=r.get("pagina"),
                    titulo=r["titulo"], detalle=r["detalle"], evidencia=r.get("evidencia") or {}, prioridad=r.get("prioridad", "media"), origen=r.get("origen"))
        if r["clave"] in existentes:
            viejas.append(base)
        else:
            nuevas.append(dict(base, estado=r.get("estado", "propuesta"), mes_alta=r["mes_alta"]))
    upsert("recomendaciones", nuevas, "clave")
    upsert("recomendaciones", viejas, "clave")
    print(f"recomendaciones: {len(nuevas)} nuevas, {len(viejas)} actualizadas (sin tocar estado)")

# ------------------------------------------------------------------ 3. métricas del mes (ventana de 31 días)
gasto_path = os.path.join(PROY, "informe", "datos_gasto_actual.json")
G = json.load(open(gasto_path, encoding="utf-8")) if os.path.exists(gasto_path) else None
if SOLO in (None, "metricas") and G:
    hasta = G["hasta"]
    mes = hasta[:7]
    acc = {}
    for f in G["filas"]:
        cid = campana_id(f["campana"])
        if not cid:
            continue
        a = acc.setdefault(cid, dict(campana_id=cid, mes=mes, coste=0.0, clics=0, impresiones=0, conversiones=0.0))
        a["coste"] += float(f["coste"]); a["clics"] += int(f["clics"]); a["impresiones"] += int(f.get("impresiones", 0) or 0); a["conversiones"] += float(f["conv"])
    for a in acc.values():
        a["coste"] = round(a["coste"], 2)
    upsert("metricas_mes", list(acc.values()), "campana_id,mes")
    print(f"métricas: {len(acc)} campañas para {mes} (ventana {G['ventana']})")

# ------------------------------------------------------------------ 4. extracciones
if SOLO in (None, "extracciones"):
    nuevas = []
    if G:
        desde, hasta = G["desde"], G["hasta"]
        corrida = datetime.fromtimestamp(os.path.getmtime(gasto_path), tz=timezone.utc).isoformat()
        nuevas.append(dict(fuente="google_ads", corrida_en=corrida, desde=desde, hasta=hasta, filas=len(G["filas"]),
                           detalle={"ventana": G["ventana"], "dias": G["dias"], "snapshot_estructura": os.path.basename(snap)}))
    diarios = glob.glob(os.path.join(PROY, "datos", "gsc-historico", "*", "*_daily.csv"))
    if diarios:
        fechas = pd.concat([pd.read_csv(p, usecols=["date"], encoding="utf-8-sig")["date"] for p in diarios])
        corrida = datetime.fromtimestamp(max(os.path.getmtime(p) for p in diarios), tz=timezone.utc).isoformat()
        nuevas.append(dict(fuente="search_console", corrida_en=corrida, desde=str(fechas.min())[:10], hasta=str(fechas.max())[:10],
                           filas=int(len(fechas)), detalle={"propiedades": len(diarios), "cortes": "queries, pages, query_page, devices, daily, queries_agg, device_total, device_date"}))
    ya = {(e["fuente"], e["hasta"]) for e in api("GET", "extracciones", params={"select": "fuente,hasta"})}
    nuevas = [n for n in nuevas if (n["fuente"], n["hasta"]) not in ya]
    if nuevas:
        api("POST", "extracciones", cuerpo=nuevas, prefer="return=minimal")
    print(f"extracciones: {len(nuevas)} nuevas")
print("listo")
