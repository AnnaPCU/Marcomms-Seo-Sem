# -*- coding: utf-8 -*-
"""
publicar.py — carga en Supabase (esquema seo_sem) lo que produce el proyecto de análisis (Optimizaciónes SEO-SEM/proyecto):
  1. campañas y grupos      ← datos/ads/api/estructura_<fecha>/{campanas,grupos}.csv (la más reciente)
  2. recomendaciones        ← informe/recomendaciones.json (lo genera scripts/exportar_recomendaciones.py)
  3. métricas por campaña   ← informe/datos_gasto_actual.json (mes en curso, del 1 al último día extraído; lo genera analisis_gasto.py)
  4. extracciones           ← fechas de los archivos de Search Console y Ads

Es idempotente: las recomendaciones que ya existen (misma clave) solo actualizan texto, evidencia y prioridad;
nunca el estado, el orden ni quién las movió. Las campañas y grupos se actualizan por nombre.

Dos modos:
  --sql salida.sql   genera un archivo SQL idempotente para correr en el SQL editor de Supabase (o por el
                     conector). No necesita ninguna clave. Es el modo recomendado.
  (sin --sql)        carga por la API REST. Requiere SUPABASE_URL y SUPABASE_SERVICE_KEY en el entorno
                     (service role key; nunca en el repo ni en Vercel).
  PROYECTO_DIR       opcional; por defecto ../Optimizaciónes SEO-SEM/proyecto relativo a este repo.
Uso: python scripts/publicar.py --sql supabase/seed/carga_2026-09.sql
     python scripts/publicar.py [--solo campanas|recomendaciones|metricas|extracciones]
"""
import glob, json, os, sys
from datetime import datetime, timezone
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROY = os.environ.get("PROYECTO_DIR") or os.path.join(os.path.dirname(REPO), "Optimizaciónes SEO-SEM", "proyecto")
SQL_OUT = sys.argv[sys.argv.index("--sql") + 1] if "--sql" in sys.argv else None
SOLO = sys.argv[sys.argv.index("--solo") + 1] if "--solo" in sys.argv else None
ESQ = "seo_sem"


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


# ══════════════════════════════════════════════════════════════ leer las fuentes
snaps = sorted(glob.glob(os.path.join(PROY, "datos", "ads", "api", "estructura_*")))
if not snaps:
    sys.exit("No hay datos/ads/api/estructura_* en el proyecto.")
snap = snaps[-1]
camp = pd.read_csv(os.path.join(snap, "campanas.csv"), encoding="utf-8-sig")
CAMPANAS = []
for _, r in camp.iterrows():
    nombre = str(r["campaign.name"])
    micros = pd.to_numeric(r.get("campaign_budget.amount_micros"), errors="coerce")
    CAMPANAS.append(dict(ads_id=str(r["campaign.id"]), nombre=nombre, marca=str(r["marca"]).upper(), unidad=unidad_de(nombre),
                         estado=str(r["campaign.status"]), presupuesto_dia=None if pd.isna(micros) else round(float(micros) / 1e6, 2)))
NOMBRES = [c["nombre"] for c in CAMPANAS]

gru = pd.read_csv(os.path.join(snap, "grupos.csv"), encoding="utf-8-sig")
c_camp, c_nom, c_id, c_est = col(gru, "campaign.name"), col(gru, "ad_group.name"), col(gru, "ad_group.id"), col(gru, "ad_group.status")
GRUPOS = [dict(campana=str(r[c_camp]), ads_id=str(r[c_id]), nombre=str(r[c_nom]), estado=str(r[c_est])) for _, r in gru.iterrows() if str(r[c_camp]) in NOMBRES]


def campana_nombre(prefijo):
    """Nombre exacto de la campaña a partir de un nombre completo o un prefijo."""
    if not prefijo:
        return None
    if prefijo in NOMBRES:
        return prefijo
    return next((n for n in NOMBRES if n.startswith(prefijo)), None)


RECS = []
ruta_recs = os.path.join(PROY, "informe", "recomendaciones.json")
if os.path.exists(ruta_recs):
    for r in json.load(open(ruta_recs, encoding="utf-8")):
        RECS.append(dict(r, campana=campana_nombre(r.get("campana"))))

gasto_path = os.path.join(PROY, "informe", "datos_gasto_actual.json")
G = json.load(open(gasto_path, encoding="utf-8")) if os.path.exists(gasto_path) else None
METRICAS = {}
if G:
    mes = G["hasta"][:7]
    for f in G["filas"]:
        n = campana_nombre(f["campana"])
        if not n:
            continue
        a = METRICAS.setdefault(n, dict(campana=n, mes=mes, coste=0.0, clics=0, impresiones=0, conversiones=0.0))
        a["coste"] += float(f["coste"]); a["clics"] += int(f["clics"]); a["impresiones"] += int(f.get("impresiones", 0) or 0); a["conversiones"] += float(f["conv"])
    for a in METRICAS.values():
        a["coste"] = round(a["coste"], 2)

EXTRACCIONES = []
if G:
    EXTRACCIONES.append(dict(fuente="google_ads", corrida_en=datetime.fromtimestamp(os.path.getmtime(gasto_path), tz=timezone.utc).isoformat(),
                             desde=G["desde"], hasta=G["hasta"], filas=len(G["filas"]),
                             detalle={"ventana": G["ventana"], "dias": G["dias"], "snapshot_estructura": os.path.basename(snap)}))
diarios = glob.glob(os.path.join(PROY, "datos", "gsc-historico", "*", "*_daily.csv"))
if diarios:
    fechas = pd.concat([pd.read_csv(p, usecols=["date"], encoding="utf-8-sig")["date"] for p in diarios])
    EXTRACCIONES.append(dict(fuente="search_console", corrida_en=datetime.fromtimestamp(max(os.path.getmtime(p) for p in diarios), tz=timezone.utc).isoformat(),
                             desde=str(fechas.min())[:10], hasta=str(fechas.max())[:10], filas=int(len(fechas)),
                             detalle={"propiedades": len(diarios), "cortes": "queries, pages, query_page, devices, daily, queries_agg, device_total, device_date"}))


# ══════════════════════════════════════════════════════════════ modo SQL
def q(v):
    """Literal SQL: None → null, números tal cual, dict/list → jsonb, texto entre comillas."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, (dict, list)):
        return "'" + json.dumps(v, ensure_ascii=False).replace("'", "''") + "'::jsonb"
    return "'" + str(v).replace("'", "''") + "'"


def sql_carga():
    out = [f"-- Carga generada por scripts/publicar.py el {datetime.now():%Y-%m-%d %H:%M}. Idempotente.", "begin;"]
    if SOLO in (None, "campanas"):
        out.append(f"-- campañas ({len(CAMPANAS)}) y grupos ({len(GRUPOS)}) · snapshot {os.path.basename(snap)}")
        for c in CAMPANAS:
            out.append(f"insert into {ESQ}.campanas (ads_id, nombre, marca, unidad, estado, presupuesto_dia) values "
                       f"({q(c['ads_id'])}, {q(c['nombre'])}, {q(c['marca'])}, {q(c['unidad'])}, {q(c['estado'])}, {q(c['presupuesto_dia'])}) "
                       f"on conflict (nombre) do update set ads_id = excluded.ads_id, marca = excluded.marca, unidad = excluded.unidad, "
                       f"estado = excluded.estado, presupuesto_dia = excluded.presupuesto_dia;")
        for g in GRUPOS:
            out.append(f"insert into {ESQ}.grupos (campana_id, ads_id, nombre, estado) values "
                       f"((select id from {ESQ}.campanas where nombre = {q(g['campana'])}), {q(g['ads_id'])}, {q(g['nombre'])}, {q(g['estado'])}) "
                       f"on conflict (campana_id, nombre) do update set ads_id = excluded.ads_id, estado = excluded.estado;")
    if SOLO in (None, "recomendaciones"):
        out.append(f"-- recomendaciones ({len(RECS)}): las nuevas entran como están; las existentes conservan estado, orden y quién las movió")
        for r in RECS:
            cid = f"(select id from {ESQ}.campanas where nombre = {q(r['campana'])})" if r["campana"] else "null"
            gid = (f"(select g.id from {ESQ}.grupos g join {ESQ}.campanas c on c.id = g.campana_id where c.nombre = {q(r['campana'])} and g.nombre = {q(r['grupo'])})"
                   if r["campana"] and r.get("grupo") else "null")
            out.append(f"insert into {ESQ}.recomendaciones (clave, marca, tipo, campana_id, grupo_id, sitio, pagina, titulo, detalle, evidencia, prioridad, estado, mes_alta, origen) values "
                       f"({q(r['clave'])}, {q(r['marca'])}, {q(r['tipo'])}, {cid}, {gid}, {q(r.get('sitio'))}, {q(r.get('pagina'))}, {q(r['titulo'])}, {q(r['detalle'])}, "
                       f"{q(r.get('evidencia') or {})}, {q(r.get('prioridad', 'media'))}, {q(r.get('estado', 'propuesta'))}, {q(r['mes_alta'])}, {q(r.get('origen'))}) "
                       f"on conflict (clave) do update set campana_id = excluded.campana_id, grupo_id = excluded.grupo_id, sitio = excluded.sitio, pagina = excluded.pagina, "
                       f"titulo = excluded.titulo, detalle = excluded.detalle, evidencia = excluded.evidencia, prioridad = excluded.prioridad, origen = excluded.origen;")
    if SOLO in (None, "metricas") and METRICAS:
        out.append(f"-- métricas ({len(METRICAS)} campañas) · {G['ventana']}")
        for m in METRICAS.values():
            out.append(f"insert into {ESQ}.metricas_mes (campana_id, mes, coste, clics, impresiones, conversiones) values "
                       f"((select id from {ESQ}.campanas where nombre = {q(m['campana'])}), {q(m['mes'])}, {q(m['coste'])}, {q(m['clics'])}, {q(m['impresiones'])}, {q(m['conversiones'])}) "
                       f"on conflict (campana_id, mes) do update set coste = excluded.coste, clics = excluded.clics, impresiones = excluded.impresiones, conversiones = excluded.conversiones;")
    if SOLO in (None, "extracciones"):
        out.append(f"-- extracciones ({len(EXTRACCIONES)})")
        for e in EXTRACCIONES:
            out.append(f"insert into {ESQ}.extracciones (fuente, corrida_en, desde, hasta, filas, detalle) select "
                       f"{q(e['fuente'])}, {q(e['corrida_en'])}, {q(e['desde'])}, {q(e['hasta'])}, {q(e['filas'])}, {q(e['detalle'])} "
                       f"where not exists (select 1 from {ESQ}.extracciones where fuente = {q(e['fuente'])} and hasta = {q(e['hasta'])});")
    out.append("commit;")
    return "\n".join(out) + "\n"


if SQL_OUT:
    os.makedirs(os.path.dirname(os.path.abspath(SQL_OUT)), exist_ok=True)
    open(SQL_OUT, "w", encoding="utf-8").write(sql_carga())
    print(f"-> {SQL_OUT}: {len(CAMPANAS)} campañas, {len(GRUPOS)} grupos, {len(RECS)} recomendaciones, {len(METRICAS)} métricas, {len(EXTRACCIONES)} extracciones")
    sys.exit(0)


# ══════════════════════════════════════════════════════════════ modo REST (service role key)
import requests  # noqa: E402

URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
if not URL or not KEY:
    sys.exit("Faltan SUPABASE_URL y SUPABASE_SERVICE_KEY en el entorno (o usá --sql salida.sql).")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "Accept-Profile": ESQ, "Content-Profile": ESQ}


def api(metodo, tabla, params=None, cuerpo=None, prefer=None):
    h = dict(H)
    if prefer:
        h["Prefer"] = prefer
    r = requests.request(metodo, f"{URL}/rest/v1/{tabla}", headers=h, params=params, json=cuerpo, timeout=60)
    if r.status_code >= 300:
        sys.exit(f"{metodo} {tabla}: {r.status_code} {r.text[:400]}")
    return r.json() if r.text else None


def upsert(tabla, filas, conflicto):
    if filas:
        api("POST", tabla, params={"on_conflict": conflicto}, cuerpo=filas, prefer="resolution=merge-duplicates,return=minimal")


if SOLO in (None, "campanas"):
    upsert("campanas", CAMPANAS, "nombre")
    print(f"campañas: {len(CAMPANAS)} (snapshot {os.path.basename(snap)})")
CAMP = {c["nombre"]: c["id"] for c in api("GET", "campanas", params={"select": "id,nombre"})}
if SOLO in (None, "campanas"):
    upsert("grupos", [dict(campana_id=CAMP[g["campana"]], ads_id=g["ads_id"], nombre=g["nombre"], estado=g["estado"]) for g in GRUPOS], "campana_id,nombre")
    print(f"grupos: {len(GRUPOS)}")
GRU = {(g["campana_id"], g["nombre"]): g["id"] for g in api("GET", "grupos", params={"select": "id,campana_id,nombre"})}

if SOLO in (None, "recomendaciones"):
    existentes = {r["clave"] for r in api("GET", "recomendaciones", params={"select": "clave"})}
    nuevas, viejas = [], []
    for r in RECS:
        cid = CAMP.get(r["campana"]) if r["campana"] else None
        gid = GRU.get((cid, r["grupo"])) if cid and r.get("grupo") else None
        base = dict(clave=r["clave"], marca=r["marca"], tipo=r["tipo"], campana_id=cid, grupo_id=gid, sitio=r.get("sitio"), pagina=r.get("pagina"),
                    titulo=r["titulo"], detalle=r["detalle"], evidencia=r.get("evidencia") or {}, prioridad=r.get("prioridad", "media"), origen=r.get("origen"))
        (viejas if r["clave"] in existentes else nuevas).append(base if r["clave"] in existentes else dict(base, estado=r.get("estado", "propuesta"), mes_alta=r["mes_alta"]))
    upsert("recomendaciones", nuevas, "clave")
    upsert("recomendaciones", viejas, "clave")
    print(f"recomendaciones: {len(nuevas)} nuevas, {len(viejas)} actualizadas (sin tocar estado)")

if SOLO in (None, "metricas") and METRICAS:
    upsert("metricas_mes", [dict(campana_id=CAMP[m["campana"]], mes=m["mes"], coste=m["coste"], clics=m["clics"], impresiones=m["impresiones"], conversiones=m["conversiones"])
                            for m in METRICAS.values()], "campana_id,mes")
    print(f"métricas: {len(METRICAS)} campañas ({G['ventana']})")

if SOLO in (None, "extracciones"):
    ya = {(e["fuente"], e["hasta"]) for e in api("GET", "extracciones", params={"select": "fuente,hasta"})}
    nuevas = [e for e in EXTRACCIONES if (e["fuente"], e["hasta"]) not in ya]
    if nuevas:
        api("POST", "extracciones", cuerpo=nuevas, prefer="return=minimal")
    print(f"extracciones: {len(nuevas)} nuevas")
print("listo")
