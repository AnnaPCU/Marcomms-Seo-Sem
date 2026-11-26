# -*- coding: utf-8 -*-
"""
credenciales.py — en la sesión en la nube, arma los archivos de acceso que leen los scripts a partir de las variables
de entorno del entorno de nube «SEO-SEM» (cada una en base64, una línea). Lo corre nube/sesion.sh al arrancar.

  SEOSEM_CLIENT_SECRET    → client_secret.json      (cliente OAuth de Google: Search Console, GA4 y Ads)
  SEOSEM_TOKEN_GSC        → token.json              (Search Console)
  SEOSEM_TOKEN_GA4        → token_ga4.json          (GA4)
  SEOSEM_GOOGLE_ADS_YAML  → google-ads.yaml         (Google Ads: developer token + refresh token)
  SEOSEM_META_ADS         → meta-ads.json           (Meta Ads, opcional)
  SEOSEM_SUPABASE_SERVICE → supabase-service.json   (carga por REST de publicar.py, opcional)

Nunca imprime valores: solo qué archivo armó y cuál falta. Los archivos quedan en la VM y están en .gitignore.
En la compu no hace falta: los archivos ya existen (nube/preparar_secretos.py arma las variables desde ellos).
"""
import base64, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPA = {
    "SEOSEM_CLIENT_SECRET": "client_secret.json",
    "SEOSEM_TOKEN_GSC": "token.json",
    "SEOSEM_TOKEN_GA4": "token_ga4.json",
    "SEOSEM_GOOGLE_ADS_YAML": "google-ads.yaml",
    "SEOSEM_META_ADS": "meta-ads.json",
    "SEOSEM_SUPABASE_SERVICE": "supabase-service.json",
}

if __name__ == "__main__":
    hechos, faltan = [], []
    for var, archivo in MAPA.items():
        valor = os.environ.get(var, "").strip().strip('"')
        destino = os.path.join(ROOT, archivo)
        if not valor:
            faltan.append(var)
            continue
        with open(destino, "wb") as f:
            f.write(base64.b64decode(valor))
        os.chmod(destino, 0o600)
        hechos.append(archivo)
    print("credenciales: " + (", ".join(hechos) or "ninguna") + (f" · faltan {', '.join(faltan)}" if faltan else ""))
