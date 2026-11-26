#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reporte_trimestral.py — datos para los reportes trimestrales MarComms (hoja SEO = Search Console, hoja Website = GA4).

Uso:
  python reporte_trimestral.py 2026-Q3            trimestre calendario completo (Q1 ene-mar, Q2 abr-jun, Q3 jul-sep, Q4 oct-dic)
  python reporte_trimestral.py 2026-Q3 --top 3    cantidad de keywords / páginas en los rankings (por defecto 5)
  python reporte_trimestral.py 2026-Q3 --paises   solo North America, separado en Estados Unidos y Canadá

Por propiedad saca:
  SEO (GSC)      Average Position, Impressions, Total Clicks, CTR (embudo impresión -> clic), top N keywords por clics
  Website (GA4)  Single Traffic = usuarios totales, Total Traffic = sesiones, Impressions = vistas de página,
                 Conversions = formularios + emails, con los filtros de ga4_export.py (gracias_real, EMAIL_REAL):
                   formularios = vistas a la página de gracias a la que redirige todo envío (Gravity Forms y HubSpot),
                   con origen en otra página del mismo sitio; emails = click_email fuera de páginas de empleo,
                   academy y reclamos. Hasta el 9 oct 2026 se sumaban click_email + form_submit en crudo, que
                   incluían el buscador y el acceso de administración (/exp-admin); el crudo y las vistas sin
                   filtrar a las páginas de gracias quedan en el JSON como referencia.
                 embudo vistas -> sesiones -> conversiones, top N páginas por vistas

Salida, una por marca (nunca un archivo común):
  informe/trimestral/<AAAA-QN>/<marca>/reporte_<marca>_<AAAA-QN>.json
  informe/trimestral/<AAAA-QN>/<marca>/reporte_<marca>_<AAAA-QN>.md

Accesos: token.json (Search Console) y token_ga4.json (GA4), ambos de tmisrahi@onepeterson.com. Solo lectura.
"""
import datetime as dt
import json, os, socket, sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

socket.setdefaulttimeout(60)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "informe", "trimestral")

EVENTOS_CONVERSION = ["click_email", "form_submit"]  # definición vieja (cruda), solo para la tabla antes/después
DEFINICION_CONVERSION = ("formularios = vistas a páginas de gracias (todo envío Gravity Forms o HubSpot redirige ahí) con "
                         "origen en otra página del mismo sitio, sin admin ni empleo/academy/reclamos (gracias_real) + "
                         "emails = click_email con pagePath fuera de empleo, academy y reclamos (EMAIL_REAL); filtros de ga4_export.py")

# (sitio de Search Console, propiedad GA4, nombre en el reporte)
PROPIEDADES = {
    "cu": [("https://argentina.controlunion.com/", "properties/512118948", "Control Union Argentina"),
           ("https://brasil.controlunion.com/", "properties/512120869", "Control Union Brasil"),
           ("https://chile.controlunion.com/", "properties/512070842", "Control Union Chile"),
           ("https://espana.controlunion.com/", "properties/512083164", "Control Union España"),
           ("https://mexico.controlunion.com/", "properties/512088729", "Control Union México"),
           ("https://northamerica.controlunion.com/", "properties/512051793", "Control Union North America"),
           ("https://peru.controlunion.com/", "properties/512089024", "Control Union Perú"),
           ("https://portugal.controlunion.com/", "properties/512089818", "Control Union Portugal")],
    "ps": [("https://americas.peterson-solutions.com/", "properties/514880041", "Peterson Solutions South America"),
           ("https://iberia.peterson-solutions.com/", "properties/514881149", "Peterson Solutions Iberia")],
}
NOMBRE = {"cu": "Control Union", "ps": "Peterson Solutions"}


def trimestre(txt):
    anio, q = txt.upper().split("-Q")
    anio, q = int(anio), int(q)
    if q not in (1, 2, 3, 4):
        sys.exit("Trimestre inválido: usar AAAA-Q1 … AAAA-Q4")
    ini = dt.date(anio, 3 * q - 2, 1)
    fin = (dt.date(anio + 1, 1, 1) if q == 4 else dt.date(anio, 3 * q + 1, 1)) - dt.timedelta(days=1)
    return ini, fin


def credenciales(archivo):
    ruta = os.path.join(ROOT, archivo)
    creds = Credentials.from_authorized_user_file(ruta)
    if not creds.valid:
        try:
            creds.refresh(Request())
        except Exception as e:
            sys.exit(f"{archivo}: el permiso venció ({e}). Reautorizar con scripts/ads_auth.py.")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return creds


def seo(gsc, sitio, ini, fin, top, pais=None):
    base = {"startDate": ini.isoformat(), "endDate": fin.isoformat(), "type": "web", "dataState": "final"}
    if pais:  # código ISO de 3 letras en minúscula, p. ej. «usa»
        base["dimensionFilterGroups"] = [{"filters": [{"dimension": "country", "operator": "equals", "expression": pais}]}]
    tot = (gsc.query(siteUrl=sitio, body=base).execute().get("rows") or [{}])[0]
    kw = gsc.query(siteUrl=sitio, body={**base, "dimensions": ["query"], "rowLimit": top}).execute().get("rows", [])
    imp, cli = round(tot.get("impressions", 0)), round(tot.get("clicks", 0))
    return {
        "average_position": round(tot.get("position", 0), 2),
        "impressions": imp,
        "total_clicks": cli,
        "ctr_pct": round(cli / imp * 100, 2) if imp else 0.0,
        "top_keywords": [{"keyword": r["keys"][0], "clicks": round(r["clicks"]),
                          "impressions": round(r["impressions"]), "position": round(r["position"], 1)} for r in kw],
    }


def website(ga, prop, sitio, ini, fin, top, pais=None):
    rango = [{"startDate": ini.isoformat(), "endDate": fin.isoformat()}]
    # pais: código ISO de 2 letras de GA4, p. ej. «US»; se suma con AND a cada filtro
    f_pais = [{"filter": {"fieldName": "countryId", "stringFilter": {"matchType": "EXACT", "value": pais}}}] if pais else []

    def filtro(*exprs):
        exprs = list(exprs) + f_pais
        return {} if not exprs else {"dimensionFilter": exprs[0] if len(exprs) == 1 else {"andGroup": {"expressions": exprs}}}

    tot = ga.runReport(property=prop, body={"dateRanges": rango, "metrics": [
        {"name": "totalUsers"}, {"name": "sessions"}, {"name": "screenPageViews"}], **filtro()}).execute()
    vals = [int(v["value"]) for v in tot["rows"][0]["metricValues"]] if tot.get("rows") else [0, 0, 0]
    usuarios, sesiones, vistas = vals

    ev = ga.runReport(property=prop, body={
        "dateRanges": rango, "dimensions": [{"name": "eventName"}], "metrics": [{"name": "eventCount"}],
        **filtro({"filter": {"fieldName": "eventName", "inListFilter": {"values": EVENTOS_CONVERSION}}}),
    }).execute()
    crudo = {e: 0 for e in EVENTOS_CONVERSION}
    for r in ev.get("rows", []):
        crudo[r["dimensionValues"][0]["value"]] = int(r["metricValues"][0]["value"])

    # import diferido: ga4_export importa PROPIEDADES de este archivo
    from ga4_export import EMAIL_REAL, PAGINA_GRACIAS, gracias_real

    def filas_de(dim, met, f):
        res = ga.runReport(property=prop, body={"dateRanges": rango, "dimensions": [{"name": dim}],
                                                "metrics": [{"name": met}], **filtro(f), "limit": 10000}).execute()
        return [(r["dimensionValues"][0]["value"], int(r["metricValues"][0]["value"])) for r in res.get("rows", [])]

    host = sitio.split("//")[1].strip("/")
    # todo formulario (Gravity Forms o HubSpot) redirige a una página de gracias: se cuentan esas vistas
    reales = {"formularios": sum(v for _, v in filas_de("eventName", "screenPageViews", gracias_real(host))),
              "emails": sum(v for _, v in filas_de("eventName", "eventCount", EMAIL_REAL))}
    gracias_sin_filtro = sum(v for _, v in filas_de("eventName", "screenPageViews", PAGINA_GRACIAS))
    conversiones = sum(reales.values())

    # top páginas por vistas, solo del dominio de la propiedad (descarta traductores, staging, «(not set)»)
    pg = ga.runReport(property=prop, body={
        "dateRanges": rango, "dimensions": [{"name": "hostName"}, {"name": "pagePath"}],
        "metrics": [{"name": "screenPageViews"}],
        **filtro({"filter": {"fieldName": "hostName", "stringFilter": {"matchType": "EXACT", "value": host}}}),
        "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}], "limit": top + 5,
    }).execute()
    paginas = [{"page": f"https://{r['dimensionValues'][0]['value']}{r['dimensionValues'][1]['value']}",
                "views": int(r["metricValues"][0]["value"])}
               for r in pg.get("rows", []) if r["dimensionValues"][1]["value"] not in ("(not set)", "")][:top]

    return {
        "single_traffic_users": usuarios,
        "total_traffic_sessions": sesiones,
        "impressions_pageviews": vistas,
        "conversions": conversiones,
        "conversions_detalle": reales,
        "conversions_crudas": {**crudo, "total": sum(crudo.values())},
        "vistas_gracias_sin_filtro": gracias_sin_filtro,
        "embudo_vista_a_sesion_pct": round(sesiones / vistas * 100, 2) if vistas else 0.0,
        "embudo_sesion_a_conversion_pct": round(conversiones / sesiones * 100, 2) if sesiones else 0.0,
        "top_pages": paginas,
    }


def n(x):
    return f"{x:,}".replace(",", ".")


def pct(x):
    return f"{x:.2f}".replace(".", ",") + " %"


def tabla_antes_despues(filas):
    L = ["| Cuenta | form_submit (crudo) | click_email (crudo) | Antes | Páginas de gracias (todas las vistas) | "
         "Formularios (página de gracias, filtrado) | Emails reales | Ahora |",
         "|---|---:|---:|---:|---:|---:|---:|---:|"]
    tot = [0] * 7
    for f in filas:
        w = f["website"]
        c, d = w["conversions_crudas"], w["conversions_detalle"]
        v = [c["form_submit"], c["click_email"], c["total"], w["vistas_gracias_sin_filtro"], d["formularios"], d["emails"],
             w["conversions"]]
        tot = [a + b for a, b in zip(tot, v)]
        L.append(f"| {f['cuenta']} | " + " | ".join(n(x) for x in v) + " |")
    if len(filas) > 1:
        L.append("| **Total** | " + " | ".join(f"**{n(x)}**" for x in tot) + " |")
    return L


def markdown(marca, q, ini, fin, filas, titulo=None, nota=()):
    L = [f"# {titulo or NOMBRE[marca]} — datos del reporte trimestral {q}",
         f"Período: {ini:%d/%m/%Y} al {fin:%d/%m/%Y} (trimestre calendario completo). "
         f"Fuentes: Google Search Console (hoja SEO) y Google Analytics 4 (hoja Website). "
         f"Extraído el {dt.date.today():%d/%m/%Y}.", "",
         "Dónde va cada dato en el reporte (una cuenta / región por reporte):", "",
         f"- Hoja **SEO**: «SEO — {q}» = Average Position, Impressions, Total Clicks · «Embudo de búsqueda — "
         "Impresión → Clic» = Impressions → Total Clicks con el CTR · «Top keywords — clics» = lista de keywords · "
         "«Generals KPIs» = gráfico de barras con Avg. Position, Impressions y Total Clicks.",
         f"- Hoja **Website**: «Website — {q}» = Single Traffic, Total Traffic, Impressions, Conversions · "
         "«Embudo de tráfico — Vista → Sesión → Conversión» = vistas → sesiones → conversiones con sus % · "
         "«Top landing pages — vistas» = lista de páginas · «Generals KPIs» = gráfico de barras con Single Traffic, "
         "Total Traffic, Impressions y Conversions.",
         "- No incluido (lo completa el creador del reporte): insights y plan de acción, diagnóstico, próximos pasos, "
         "glosario y el casillero «Deals generados — HubSpot».", "", *nota,
         "### Qué cuenta como «Conversions»", "",
         "Conversions = **formularios + emails**: alguien completó un formulario o hizo clic en un email (mailto).", "",
         "- **Formularios**: todo formulario del sitio, de Gravity Forms o de HubSpot, redirige al enviarse a una "
         "página de gracias (gracias / thank-you / obrigado / agradecemos). Se cuentan las vistas a esas páginas "
         "**cuando se llegó desde otra página del mismo sitio**, que es como se ve un envío. Las entradas directas "
         "sin página de origen (revisiones del equipo y robots, ~60 % de las vistas a esas páginas en el 3T 2026) "
         "quedan afuera, igual que las que vienen del administrador del sitio, de empleo, academy o reclamos.",
         "- **Emails**: evento click_email, salvo los que salen de páginas de empleo (vacantes, vagas, carreiras, "
         "careers), de la academia de cursos (academy) y de reclamos.", "",
         "No se usa el evento form_submit: además de formularios registraba el buscador del sitio y el acceso de "
         "administración (/exp-admin), y no ve los formularios de HubSpot (van dentro de un iframe).", "",
         "Límites: la página de gracias cuenta vistas, no envíos únicos (si alguien la recarga, suma dos), y si el "
         "navegador no informa la página de origen el envío no se cuenta. La columna «todas las vistas» muestra el "
         "techo sin filtrar. La pestaña «Sitios · GA4» del tablero todavía cuenta los formularios con form_submit "
         "«gform_» y no suma las páginas de gracias.", "",
         "Hasta el 9 oct 2026 este reporte sumaba click_email + form_submit en crudo, lo que inflaba la cifra. "
         "Comparación por sitio:", "",
         *tabla_antes_despues(filas), ""]
    for f in filas:
        s, w = f["seo"], f["website"]
        L += [f"## {f['cuenta']}", "",
              "### SEO — Search Console", "",
              "| Average Position | Impressions | Total Clicks | CTR (impresión → clic) |", "|---:|---:|---:|---:|",
              f"| {str(s['average_position']).replace('.', ',')} | {n(s['impressions'])} | {n(s['total_clicks'])} | {pct(s['ctr_pct'])} |",
              "", "Top keywords por clics:", ""]
        L += [f"{i}. {k['keyword']} — {n(k['clicks'])}" for i, k in enumerate(s["top_keywords"], 1)] or ["(sin datos)"]
        d = w["conversions_detalle"]
        L += ["", "### Website — Google Analytics 4", "",
              "| Single Traffic | Total Traffic | Impressions | Conversions |", "|---:|---:|---:|---:|",
              f"| {n(w['single_traffic_users'])} | {n(w['total_traffic_sessions'])} | {n(w['impressions_pageviews'])} | {n(w['conversions'])} |",
              "",
              f"Conversions = formularios por página de gracias ({n(d['formularios'])}) + emails ({n(d['emails'])}). "
              f"Con la definición anterior (click_email + form_submit en crudo) daba {n(w['conversions_crudas']['total'])}.",
              f"Embudo: vistas {n(w['impressions_pageviews'])} → sesiones {n(w['total_traffic_sessions'])} "
              f"({pct(w['embudo_vista_a_sesion_pct'])}) → conversiones {n(w['conversions'])} "
              f"({pct(w['embudo_sesion_a_conversion_pct'])} de las sesiones).",
              "", "Top páginas por vistas:", ""]
        L += [f"{i}. {p['page']} — {n(p['views'])}" for i, p in enumerate(w["top_pages"], 1)] or ["(sin datos)"]
        L.append("")
    return "\n".join(L)


# North America junta Estados Unidos y Canadá en un mismo sitio: se separa por país (GSC usa ISO-3, GA4 ISO-2)
PAISES_NA = [("Estados Unidos", "usa", "US"), ("Canadá", "can", "CA")]


def norteamerica_por_pais(gsc, ga, q, ini, fin, top):
    sitio, prop, cuenta = next(x for x in PROPIEDADES["cu"] if "northamerica" in x[0])
    total = {"seo": seo(gsc, sitio, ini, fin, top), "website": website(ga, prop, sitio, ini, fin, top)}
    filas = []
    for nombre, iso3, iso2 in PAISES_NA:
        fila = {"cuenta": f"{cuenta} — {nombre}", "pais": nombre, "search_console": sitio, "ga4": prop,
                "filtro_pais": {"search_console": iso3, "ga4": iso2},
                "seo": seo(gsc, sitio, ini, fin, top, pais=iso3), "website": website(ga, prop, sitio, ini, fin, top, pais=iso2)}
        filas.append(fila)
        print(f"  {fila['cuenta']:<46} SEO {fila['seo']['total_clicks']:>5} clics · Web {fila['website']['total_traffic_sessions']:>5} "
              f"sesiones, {fila['website']['conversions']:>4} conversiones")

    def resto(clave, campo):
        return total[clave][campo] - sum(f[clave][campo] for f in filas)

    filas_conc = [("Clics (SEO)", "seo", "total_clicks"), ("Impresiones (SEO)", "seo", "impressions"),
                  ("Sesiones (Website)", "website", "total_traffic_sessions"),
                  ("Vistas de página (Website)", "website", "impressions_pageviews"),
                  ("Conversiones (Website)", "website", "conversions")]
    nota = ["**Este archivo separa el sitio northamerica.controlunion.com por país** (Estados Unidos y Canadá), "
            "con los mismos datos que el resto de las cuentas. Cada país se arma como un reporte propio.", "",
            "Estados Unidos + Canadá no suman el total del sitio: el resto del tráfico viene de otros países. "
            "Usuarios y posición promedio no se pueden sumar ni restar entre países.", "",
            "| Métrica | Total sitio | Estados Unidos | Canadá | Otros países |", "|---|---:|---:|---:|---:|"]
    nota += [f"| {et} | {n(total[c][k])} | {n(filas[0][c][k])} | {n(filas[1][c][k])} | {n(resto(c, k))} |"
             for et, c, k in filas_conc]
    nota.append("")

    carpeta = os.path.join(OUT, q, "cu")
    os.makedirs(carpeta, exist_ok=True)
    base = os.path.join(carpeta, f"reporte_cu_{q}_northamerica_por_pais")
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump({"marca": NOMBRE["cu"], "trimestre": q, "desde": ini.isoformat(), "hasta": fin.isoformat(),
                   "extraido": dt.date.today().isoformat(), "definicion_conversion": DEFINICION_CONVERSION,
                   "total_sitio": total, "cuentas": filas}, f, ensure_ascii=False, indent=2)
    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write(markdown("cu", q, ini, fin, filas, titulo="Control Union North America por país", nota=nota))
    print(f"  -> {os.path.relpath(base, ROOT)}.json / .md")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    q = args[0].upper()
    top = int(args[args.index("--top") + 1]) if "--top" in args else 5
    ini, fin = trimestre(q)
    if fin >= dt.date.today() - dt.timedelta(days=3):
        print(f"AVISO: {q} termina el {fin}; Search Console todavía no tiene datos finales de los últimos días.")
    gsc = build("searchconsole", "v1", credentials=credenciales("token.json"), cache_discovery=False).searchanalytics()
    ga = build("analyticsdata", "v1beta", credentials=credenciales("token_ga4.json"), cache_discovery=False).properties()

    if "--paises" in args:
        return norteamerica_por_pais(gsc, ga, q, ini, fin, top)

    for marca, props in PROPIEDADES.items():
        filas = []
        for sitio, prop, cuenta in props:
            print(f"  {cuenta:<34}", end=" ", flush=True)
            fila = {"cuenta": cuenta, "search_console": sitio, "ga4": prop,
                    "seo": seo(gsc, sitio, ini, fin, top), "website": website(ga, prop, sitio, ini, fin, top)}
            filas.append(fila)
            print(f"SEO {fila['seo']['total_clicks']:>6} clics · Web {fila['website']['total_traffic_sessions']:>6} sesiones, "
                  f"{fila['website']['conversions']:>4} conversiones")
        carpeta = os.path.join(OUT, q, marca)
        os.makedirs(carpeta, exist_ok=True)
        base = os.path.join(carpeta, f"reporte_{marca}_{q}")
        with open(base + ".json", "w", encoding="utf-8") as f:
            json.dump({"marca": NOMBRE[marca], "trimestre": q, "desde": ini.isoformat(), "hasta": fin.isoformat(),
                       "extraido": dt.date.today().isoformat(), "definicion_conversion": DEFINICION_CONVERSION,
                       "cuentas": filas}, f, ensure_ascii=False, indent=2)
        with open(base + ".md", "w", encoding="utf-8") as f:
            f.write(markdown(marca, q, ini, fin, filas))
        print(f"  -> {os.path.relpath(base, ROOT)}.json / .md")


if __name__ == "__main__":
    main()
