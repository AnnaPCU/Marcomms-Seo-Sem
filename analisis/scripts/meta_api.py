# -*- coding: utf-8 -*-
"""
meta_api.py — cliente mínimo de la Marketing API de Meta (Graph API), compartido por meta_export.py y meta_subir.py.

Credenciales en analisis/meta-ads.json (no se sube a ningún lado ni se pega en el chat):
  {
    "access_token": "<token de usuario del sistema, rol Empleado>",
    "version": "v26.0",
    "cuentas": {"act_1234567890": "CU"}                // cuenta → marca (CU | PS | PCU). Cada cuenta es de una sola marca y
                                                       // de acá sale la marca de todo lo que trae. Si falta, se usan todas las
                                                       // cuentas que ve el token y la marca sale del prefijo del nombre.
  }
También acepta la variable de entorno META_ACCESS_TOKEN, que tiene prioridad sobre el archivo.

Maneja paginado, límites de uso (espera según el encabezado x-business-use-case-usage) y reintentos.
"""
import json, os, sys, time
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "meta-ads.json")
GRAPH = "https://graph.facebook.com"
# errores de límite de uso o transitorios: se espera y se reintenta
LIMITE = {4, 17, 32, 613, 80000, 80001, 80002, 80003, 80004, 80005, 80006, 80008, 80009, 80014}
TRANSITORIO = {1, 2}


def config():
    c = json.load(open(CONFIG, encoding="utf-8")) if os.path.exists(CONFIG) else {}
    c["access_token"] = os.environ.get("META_ACCESS_TOKEN") or c.get("access_token")
    c.setdefault("version", "v26.0")
    if not c["access_token"]:
        sys.exit(f"Falta el token: crear {CONFIG} (ver META_ADS.md) o definir META_ACCESS_TOKEN.")
    return c


class Meta:
    def __init__(self):
        self.c = config()
        self.base = f"{GRAPH}/{self.c['version']}"

    def _pedir(self, metodo, ruta, params=None, data=None, files=None, intentos=6):
        url = ruta if ruta.startswith("http") else f"{self.base}/{ruta.lstrip('/')}"
        params = dict(params or {})
        if not ruta.startswith("http"):
            params["access_token"] = self.c["access_token"]
        for i in range(intentos):
            r = requests.request(metodo, url, params=params, data=data, files=files, timeout=120)
            self._esperar_si_hace_falta(r)
            if r.ok:
                return r.json()
            err = (r.json() if r.headers.get("content-type", "").startswith("application/json") else {}).get("error", {})
            codigo = err.get("code")
            if (codigo in LIMITE or codigo in TRANSITORIO or r.status_code >= 500) and i < intentos - 1:
                espera = 60 * (i + 1) if codigo in LIMITE else 5 * (i + 1)
                print(f"  … {codigo} {err.get('message', '')[:80]}: espero {espera}s", file=sys.stderr)
                time.sleep(espera)
                continue
            raise RuntimeError(f"{metodo} {ruta}: {r.status_code} {json.dumps(err, ensure_ascii=False)[:600]}")

    @staticmethod
    def _esperar_si_hace_falta(r):
        """si alguna cuenta pasó el 85% del cupo, espera lo que Meta indica (estimated_time_to_regain_access, en minutos)"""
        uso = r.headers.get("x-business-use-case-usage")
        if not uso:
            return
        try:
            for lista in json.loads(uso).values():
                for u in lista:
                    if max(u.get("call_count", 0), u.get("total_cputime", 0), u.get("total_time", 0)) >= 85:
                        minutos = max(1, int(u.get("estimated_time_to_regain_access") or 1))
                        print(f"  … cupo al {u.get('call_count')}%: espero {minutos} min", file=sys.stderr)
                        time.sleep(60 * minutos)
                        return
        except (ValueError, AttributeError):
            pass

    def get(self, ruta, **params):
        return self._pedir("GET", ruta, params)

    def todos(self, ruta, **params):
        """recorre el paginado y devuelve la lista completa de 'data'"""
        params.setdefault("limit", 200)
        out, r = [], self._pedir("GET", ruta, params)
        while True:
            out.extend(r.get("data", []))
            sig = (r.get("paging") or {}).get("next")
            if not sig:
                return out
            r = self._pedir("GET", sig)

    def post(self, ruta, data=None, files=None):
        datos = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in (data or {}).items()}
        return self._pedir("POST", ruta, data=datos, files=files, intentos=3)

    def informe_async(self, cuenta, **params):
        """insights grandes: crea el informe asíncrono, espera a que termine y devuelve todas las filas"""
        run = self.post(f"{cuenta}/insights", params)["report_run_id"]
        while True:
            s = self.get(run, fields="async_status,async_percent_completion")
            if s["async_status"] == "Job Completed":
                return self.todos(f"{run}/insights")
            if s["async_status"] in ("Job Failed", "Job Skipped"):
                raise RuntimeError(f"informe {run}: {s['async_status']}")
            time.sleep(5)

    def cuentas(self):
        """cuentas publicitarias a extraer: las de meta-ads.json o, si no hay, todas las que ve el token"""
        if self.c.get("cuentas"):
            return list(self.c["cuentas"])
        return [a["id"] for a in self.todos("me/adaccounts", fields="id")]


def marca_de(nombre):
    n = str(nombre)
    return "cu" if n.startswith(("CU ", "CU_", "CUC ", "CUC_")) else ("ps" if n.startswith(("PS ", "PS_")) else ("pcu" if n.startswith(("PCU ", "PCU_")) else "otros"))
