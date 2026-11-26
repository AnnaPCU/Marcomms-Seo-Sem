# -*- coding: utf-8 -*-
"""
ga4_paginas.py — vistas por página de cada sitio de Control Union, desde GA4 (solo lectura, token_ga4.json).

Sirve para medir cuánto tráfico reciben las landings de industrias y de programas de certificación frente
al resto del sitio (análisis de oct 2026: ¿vale la pena ponerles formulario de HubSpot?).

Uso:
  python ga4_paginas.py                      desde el inicio del histórico (dic 2025) hasta ayer
  python ga4_paginas.py 2026-07-01 2026-09-30
Salida: informe/datos_ga4_paginas.json  {desde, hasta, dias, sitios: {host: [{ruta, vistas, sesiones, interaccion, usuarios}]}}
"""
import datetime as dt, json, os, socket, sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

socket.setdefaulttimeout(120)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from reporte_trimestral import PROPIEDADES


def credenciales():
    c = Credentials.from_authorized_user_file(os.path.join(ROOT, "token_ga4.json"))
    c.refresh(Request())
    return c


def paginas(ga, prop, desde, hasta):
    filas, offset, out = None, 0, []
    while True:
        cuerpo = {"dateRanges": [{"startDate": desde, "endDate": hasta}],
                  "dimensions": [{"name": "pagePath"}],
                  "metrics": [{"name": m} for m in ("screenPageViews", "sessions", "engagedSessions", "totalUsers")],
                  "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}],
                  "limit": 100000, "offset": offset}
        r = ga.runReport(property=prop, body=cuerpo).execute()
        filas = r.get("rows", [])
        for f in filas:
            v = [int(float(m["value"])) for m in f["metricValues"]]
            out.append({"ruta": f["dimensionValues"][0]["value"], "vistas": v[0], "sesiones": v[1], "interaccion": v[2], "usuarios": v[3]})
        offset += len(filas)
        if offset >= int(r.get("rowCount", 0)) or not filas:
            break
    return out


def main():
    ayer = dt.date.today() - dt.timedelta(days=1)
    desde = sys.argv[1] if len(sys.argv) > 1 else "2025-12-01"
    hasta = sys.argv[2] if len(sys.argv) > 2 else str(ayer)
    dias = (dt.date.fromisoformat(hasta) - dt.date.fromisoformat(desde)).days + 1
    ga = build("analyticsdata", "v1beta", credentials=credenciales(), cache_discovery=False).properties()
    salida = {"desde": desde, "hasta": hasta, "dias": dias, "sitios": {}}
    for sitio, prop, nombre in PROPIEDADES["cu"]:
        host = sitio.split("//")[1].rstrip("/")
        filas = paginas(ga, prop, desde, hasta)
        salida["sitios"][host] = filas
        print(f"{nombre:30} {len(filas):>5} rutas · {sum(f['vistas'] for f in filas):>7} vistas")
    ruta = os.path.join(ROOT, "informe", "datos_ga4_paginas.json")
    json.dump(salida, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"-> {ruta}")


if __name__ == "__main__":
    main()
