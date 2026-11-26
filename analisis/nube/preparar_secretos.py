# -*- coding: utf-8 -*-
"""
preparar_secretos.py — EN LA COMPU (una vez, o cuando se renueve un acceso): arma nube/secretos_nube.env.local con las
variables SEOSEM_* que espera nube/credenciales.py, cada archivo de acceso en base64 en una sola línea.

Uso: python nube/preparar_secretos.py
Después: abrir nube/secretos_nube.env.local, copiar todo y pegarlo en claude.ai/code → entorno «SEO-SEM» → Environment
variables. Borrar el archivo al terminar. No se sube a GitHub (*.local está en .gitignore) y nunca se pega en un chat.
"""
import base64, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credenciales import MAPA, ROOT  # noqa: E402

salida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "secretos_nube.env.local")
lineas = []
for var, archivo in MAPA.items():
    p = os.path.join(ROOT, archivo)
    if os.path.exists(p):
        lineas.append(f"{var}={base64.b64encode(open(p, 'rb').read()).decode()}")
        print(f"  {var}: {archivo} ({os.path.getsize(p)} bytes)")
    else:
        print(f"  {var}: no existe {archivo} (se omite)")
open(salida, "w", encoding="utf-8").write("\n".join(lineas) + "\n")
print(f"Listo: {salida} ({len(lineas)} variables). Pegalas en el entorno de nube y borrá el archivo.")
