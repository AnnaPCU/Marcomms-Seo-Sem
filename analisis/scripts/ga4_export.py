# -*- coding: utf-8 -*-
"""
ga4_export.py — métricas limpias de Google Analytics 4 por sitio y por mes, para la pestaña «Sitios» del tablero
(solo lectura, token_ga4.json de tmisrahi@onepeterson.com).

Limpieza (validación del 9 oct 2026):
  · Visitas: se reporta «con interacción» (engagedSessions) además de las sesiones, porque hay tráfico de bots
    (visitas directas desde Singapur, China, EE.UU. de 3 segundos y ~5% de interacción) que infla las sesiones.
  · Contactos reales = formularios del sitio (form_submit con form_id «gform_…», Gravity Forms) + clics a email que NO
    salen de páginas de empleo (vacantes, vagas, carreiras, careers), de la academia de cursos ni de reclamos. Se descartan form_submit del buscador y del acceso de administración (/exp-admin) y los
    click_email de vacantes: en el 3T 2026 eran 517 de 528 form_submit.
  · Los formularios de HubSpot embebidos (iframe) no llegan a GA4: no están en estos números.

Uso:
  python ga4_export.py                 mes anterior completo + mes en curso hasta ayer
  python ga4_export.py 2026-09         un mes
  python ga4_export.py 2025-12 2026-10 un rango de meses (el histórico arranca en dic 2025: antes no hay datos)
Salida: informe/datos_ga4.json  (lista de {sitio, marca, nombre, mes, desde, hasta, datos}). Se suma a lo que ya tiene
el archivo: cada corrida reemplaza solo los sitio-mes que extrae.
"""
import calendar, datetime as dt, json, os, socket, sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

socket.setdefaulttimeout(60)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from reporte_trimestral import PROPIEDADES  # mismo mapeo sitio ↔ propiedad que el reporte trimestral

# no son contactos comerciales: empleo (es/pt/en), academia de cursos y reclamos
EMPLEO = r".*(vacan|vacanc|vaga|carreira|career|empleo|trabaj|job|academy|complaint|reclam).*"


def credenciales():
    c = Credentials.from_authorized_user_file(os.path.join(ROOT, "token_ga4.json"))
    c.refresh(Request())
    return c


def filtro_y(*filtros):
    return {"andGroup": {"expressions": list(filtros)}}


def ev(nombre):
    return {"filter": {"fieldName": "eventName", "stringFilter": {"value": nombre}}}


def no(f):
    return {"notExpression": f}


FORM_REAL = filtro_y(ev("form_submit"), {"filter": {"fieldName": "customEvent:form_id", "stringFilter": {"matchType": "BEGINS_WITH", "value": "gform_"}}})
EMAIL_REAL = filtro_y(ev("click_email"), no({"filter": {"fieldName": "pagePath", "stringFilter": {"matchType": "FULL_REGEXP", "value": EMPLEO, "caseSensitive": False}}}))

# Formularios por página de gracias: todo envío, de Gravity Forms o de HubSpot (iframe, GA4 no ve el envío),
# redirige a una página de gracias del sitio (confirmado por Felipe, 9 oct 2026). Es la medida de formularios
# del reporte trimestral. Cuenta solo si se llegó desde otra página del mismo sitio: las entradas directas sin
# origen son revisiones del equipo y robots (en el 3T 2026, ~60% de las vistas). Se descartan orígenes de
# administración, de otra página de gracias y de empleo / academy / reclamos.
# Todavía no lo usa la pestaña «Sitios · GA4», que sigue con FORM_REAL (oct 2026).
GRACIAS = r".*(thank|gracias|obrigad|agradec).*"
REF_DESCARTE = r".*(thank|gracias|obrigad|agradec|wp-admin|wp-login|exp-admin|vacan|vaga|carreira|career|empleo|trabaj|job|academy|complaint|reclam).*"
PAGINA_GRACIAS = {"filter": {"fieldName": "pagePath", "stringFilter": {"matchType": "FULL_REGEXP", "value": GRACIAS, "caseSensitive": False}}}


def gracias_real(host):
    return filtro_y(PAGINA_GRACIAS,
                    {"filter": {"fieldName": "pageReferrer", "stringFilter": {"matchType": "BEGINS_WITH", "value": f"https://{host}/"}}},
                    no({"filter": {"fieldName": "pageReferrer", "stringFilter": {"matchType": "FULL_REGEXP", "value": REF_DESCARTE, "caseSensitive": False}}}))


def correr(ga, prop, rango, dims, mets, filtro=None, orden=None, limite=None):
    cuerpo = {"dateRanges": [rango], "dimensions": [{"name": d} for d in dims], "metrics": [{"name": m} for m in mets]}
    if filtro:
        cuerpo["dimensionFilter"] = filtro
    if orden:
        cuerpo["orderBys"] = [{"metric": {"metricName": orden}, "desc": True}]
    if limite:
        cuerpo["limit"] = limite
    filas = ga.runReport(property=prop, body=cuerpo).execute().get("rows", [])
    return [([d["value"] for d in f.get("dimensionValues", [])], [float(m["value"]) for m in f["metricValues"]]) for f in filas]


def sitio_mes(ga, prop, desde, hasta):
    r = {"startDate": desde, "endDate": hasta}
    t = correr(ga, prop, r, [], ["sessions", "engagedSessions", "totalUsers", "screenPageViews", "averageSessionDuration"])
    s, e, u, v, dur = t[0][1] if t else (0, 0, 0, 0, 0)
    canales = {d[0]: {"sesiones": int(m[0]), "interaccion": int(m[1])}
               for d, m in correr(ga, prop, r, ["sessionDefaultChannelGroup"], ["sessions", "engagedSessions"])}
    contactos = {}
    for tipo, f in (("formularios", FORM_REAL), ("emails", EMAIL_REAL)):
        for d, m in correr(ga, prop, r, ["sessionDefaultChannelGroup"], ["eventCount"], f):
            contactos.setdefault(d[0], {"formularios": 0, "emails": 0})[tipo] = int(m[0])
    def landings(canal_filtro):
        return [{"pagina": d[0], "sesiones": int(m[0]), "interaccion": int(m[1])}
                for d, m in correr(ga, prop, r, ["landingPage"], ["sessions", "engagedSessions"], canal_filtro, "sessions", 8)]
    pagas = landings({"filter": {"fieldName": "sessionDefaultChannelGroup", "stringFilter": {"value": "Paid Search"}}})
    organicas = landings({"filter": {"fieldName": "sessionDefaultChannelGroup", "stringFilter": {"value": "Organic Search"}}})
    # bots probables: sesiones directas sin interacción
    directo = canales.get("Direct", {"sesiones": 0, "interaccion": 0})
    return {"sesiones": int(s), "interaccion": int(e), "usuarios": int(u), "vistas": int(v), "duracion_media": round(dur),
            "canales": canales, "contactos": contactos,
            "contactos_total": sum(c["formularios"] + c["emails"] for c in contactos.values()),
            "directo_sin_interaccion": directo["sesiones"] - directo["interaccion"],
            "landings_pagas": pagas, "landings_organicas": organicas}


def rangos(arg, arg_hasta=None):
    ayer = dt.date.today() - dt.timedelta(days=1)
    if arg:
        a, m = map(int, arg.split("-"))
        a2, m2 = map(int, (arg_hasta or arg).split("-"))
        out = []
        while (a, m) <= (a2, m2):
            fin = min(dt.date(a, m, calendar.monthrange(a, m)[1]), ayer)
            out.append((f"{a}-{m:02d}", dt.date(a, m, 1), fin))
            a, m = (a + 1, 1) if m == 12 else (a, m + 1)
        return out
    ini_actual = ayer.replace(day=1)
    fin_ant = ini_actual - dt.timedelta(days=1)
    out = [(f"{fin_ant:%Y-%m}", fin_ant.replace(day=1), fin_ant)]
    if ayer >= ini_actual:
        out.append((f"{ayer:%Y-%m}", ini_actual, ayer))
    return out


def main():
    ga = build("analyticsdata", "v1beta", credentials=credenciales(), cache_discovery=False).properties()
    salida = []
    for mes, desde, hasta in rangos(sys.argv[1] if len(sys.argv) > 1 else None, sys.argv[2] if len(sys.argv) > 2 else None):
        for marca, lista in PROPIEDADES.items():
            for sitio, prop, nombre in lista:
                datos = sitio_mes(ga, prop, str(desde), str(hasta))
                salida.append(dict(sitio=sitio.split("//")[1].rstrip("/"), marca=marca.upper(), nombre=nombre, propiedad=prop,
                                   mes=mes, desde=str(desde), hasta=str(hasta), dias=(hasta - desde).days + 1, datos=datos))
                print(f"{mes} {nombre[:34]:34} sesiones {datos['sesiones']:>5} · con interacción {datos['interaccion']:>5} · contactos reales {datos['contactos_total']}")
    ruta = os.path.join(ROOT, "informe", "datos_ga4.json")
    nuevos = {(x["sitio"], x["mes"]) for x in salida}
    previos = json.load(open(ruta, encoding="utf-8")) if os.path.exists(ruta) else []
    todo = sorted([x for x in previos if (x["sitio"], x["mes"]) not in nuevos] + salida, key=lambda x: (x["mes"], x["marca"], x["nombre"]))
    json.dump(todo, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"-> {ruta} ({len(salida)} sitio-mes nuevos, {len(todo)} en total)")


if __name__ == "__main__":
    main()
