#!/usr/bin/env bash
# Arranque de cada sesión en la nube (hook SessionStart de .claude/settings.json del repo). En la compu no hace nada.
# 1) dependencias de Python si el setup del entorno no las dejó instaladas, 2) descomprime los CSV grandes de datos/,
# 3) arma los archivos de acceso desde las variables SEOSEM_* (nube/credenciales.py). Nunca imprime secretos.
if [ "$CLAUDE_CODE_REMOTE" != "true" ]; then exit 0; fi
cd "$CLAUDE_PROJECT_DIR/analisis" || exit 0
# la VM corre en UTC: los scripts fechan en hora de Argentina («hoy», «Extraído: … hora de Argentina»)
export TZ=America/Argentina/Buenos_Aires
if [ -n "$CLAUDE_ENV_FILE" ]; then echo "export TZ=America/Argentina/Buenos_Aires" >> "$CLAUDE_ENV_FILE"; fi
if ! python3 -c "import pandas, google.ads.googleads, googleapiclient, yaml" 2>/dev/null; then
  pip install -q --break-system-packages -r requirements.txt >/tmp/pip_seosem.log 2>&1 \
    || pip install -q -r requirements.txt >>/tmp/pip_seosem.log 2>&1 \
    || echo "pip falló: ver /tmp/pip_seosem.log"
fi
python3 scripts/datos_gz.py descomprimir
python3 nube/credenciales.py
exit 0
