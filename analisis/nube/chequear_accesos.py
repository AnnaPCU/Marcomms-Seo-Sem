# -*- coding: utf-8 -*-
"""
chequear_accesos.py — comprueba, con una consulta chica de solo lectura por fuente, que los accesos del proyecto andan:
Google Ads, Search Console, GA4 y Meta Ads. Lo corren primero las tareas programadas de la nube (nube/TAREAS.md) para
frenar antes de extraer si un token venció, y sirve igual en la compu.

  python nube/chequear_accesos.py            (desde analisis/)

Nunca imprime tokens ni el contenido de los archivos de acceso, y no los reescribe (el token renovado queda en memoria).
Sale con código 1 si alguna fuente falla; cada línea dice OK o FALLA con el motivo.
"""
import datetime as dt, json, os, socket, sys

socket.setdefaulttimeout(60)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

SITIO_GSC = "https://argentina.controlunion.com/"
PROPIEDAD_GA4 = "properties/512118948"


def google_ads():
    from google.ads.googleads.client import GoogleAdsClient
    cuentas = json.load(open(os.path.join(ROOT, "google-ads.cuentas.json"), encoding="utf-8"))
    cid = cuentas["cuentas"]["principal"]
    svc = GoogleAdsClient.load_from_storage(os.path.join(ROOT, "google-ads.yaml")).get_service("GoogleAdsService")
    q = "SELECT customer.descriptive_name, customer.currency_code FROM customer LIMIT 1"
    for lote in svc.search_stream(customer_id=str(cid), query=q):
        for r in lote.results:
            return f"cuenta {cid} «{r.customer.descriptive_name}» ({r.customer.currency_code})"
    raise RuntimeError("la consulta no devolvió la cuenta")


def credencial(archivo, scopes=None):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    c = Credentials.from_authorized_user_file(os.path.join(ROOT, archivo), scopes)
    if not c.valid:
        c.refresh(Request())
    return c


def search_console():
    from googleapiclient.discovery import build
    c = credencial("token.json", ["https://www.googleapis.com/auth/webmasters.readonly"])
    sc = build("searchconsole", "v1", credentials=c, cache_discovery=False)
    hoy = dt.date.today()
    r = sc.searchanalytics().query(siteUrl=SITIO_GSC, body={
        "startDate": str(hoy - dt.timedelta(days=16)), "endDate": str(hoy), "dimensions": ["date"]}).execute()
    filas = sorted(r.get("rows", []), key=lambda x: x["keys"][0])
    if not filas:
        raise RuntimeError(f"sin filas para {SITIO_GSC} en los últimos 16 días")
    return f"{SITIO_GSC} · último día publicado {filas[-1]['keys'][0]}"


def ga4():
    from googleapiclient.discovery import build
    ga = build("analyticsdata", "v1beta", credentials=credencial("token_ga4.json"), cache_discovery=False).properties()
    r = ga.runReport(property=PROPIEDAD_GA4, body={"dateRanges": [{"startDate": "7daysAgo", "endDate": "yesterday"}],
                                                    "metrics": [{"name": "sessions"}]}).execute()
    sesiones = (r.get("rows") or [{}])[0].get("metricValues", [{}])[0].get("value", "0")
    return f"{PROPIEDAD_GA4} · {sesiones} sesiones en los últimos 7 días"


def meta():
    from meta_api import Meta
    m = Meta()
    cuentas = m.todos("me/adaccounts", fields="id")
    return f"{len(cuentas)} cuentas visibles · {m.c['version']}"


def motivo(e):
    texto = " ".join(str(e).split())
    if "invalid_grant" in texto:
        texto = "invalid_grant: el permiso venció o se revocó (reautorizar, ver nube/LEEME.md)"
    return texto[:300]


if __name__ == "__main__":
    fallas = 0
    for nombre, prueba in (("Google Ads", google_ads), ("Search Console", search_console), ("GA4", ga4),
                           ("Meta Ads", meta)):
        try:
            print(f"{nombre}: OK · {prueba()}")
        except SystemExit as e:
            fallas += 1
            print(f"{nombre}: FALLA · {e}")
        except Exception as e:  # noqa: BLE001 — se informa cualquier error de la fuente y se sigue con la próxima
            fallas += 1
            print(f"{nombre}: FALLA · {type(e).__name__}: {motivo(e)}")
    sys.exit(1 if fallas else 0)
