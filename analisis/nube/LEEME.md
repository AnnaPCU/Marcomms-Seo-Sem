# Proyecto SEO-SEM en sesiones en la nube

El proyecto de análisis vive en `analisis/` del repo AnnaPCU/Marcomms-Seo-Sem. Así se puede abrir como sesión en la
nube (claude.ai/code), igual que MarComms Hub, sin depender de que la compu de Felipe esté prendida.

## Cómo funciona

- **Código y datos:** vienen con el repo.
  - Los CSV de más de 5 MB viajan comprimidos (`.csv.gz`); ver `scripts/datos_gz.py`.
  - Al arrancar cada sesión, `nube/sesion.sh` (hook SessionStart de `.claude/settings.json`) hace tres cosas: instala las dependencias si faltan, descomprime los CSV y arma los archivos de acceso.
- **Accesos de Google y Meta:** salen de variables del entorno de nube «SEO-SEM» (`SEOSEM_*`, cada una en base64). `nube/credenciales.py` los escribe en la VM; nunca van al repo.
- **Supabase:** por el conector de claude.ai, con el SQL que genera `scripts/publicar.py --sql` (regla 4 del
  `CLAUDE.md` de la raíz: sin service role key). En la nube no hace falta `SEOSEM_SUPABASE_SERVICE`.
- **Tareas programadas:** corren en este entorno, cada una en una sesión nueva: ver `nube/TAREAS.md`.
- **Hora:** la VM está en UTC; el arranque fija `TZ=America/Argentina/Buenos_Aires` para toda la sesión.
- **En la compu nada cambia:** el hook no hace nada fuera de la nube y los archivos de acceso siguen en la carpeta.

## Configuración (una sola vez, la hace Felipe en claude.ai/code)

1. **Preparar las variables, en la compu:** `python nube/preparar_secretos.py` (desde `analisis/`). Escribe `nube/secretos_nube.env.local`, que no se sube a GitHub.
2. **Crear el entorno:** en claude.ai/code, en el selector de entorno debajo del cuadro de mensaje, agregá un entorno nuevo llamado **SEO-SEM**. No uses «Default»: es el de MarComms Hub, y quien use un entorno puede leer sus variables.
3. **Environment variables:** pegá todo el contenido de `nube/secretos_nube.env.local`. Después borrá ese archivo de la compu.
4. **Network access:** «Limited» con «Allow package managers» tildado. En «Allowed domains» agregá:
   ```
   graph.facebook.com
   *.supabase.co
   ```
   Las APIs de Google (`*.googleapis.com`) y PyPI ya están en la lista por defecto.
5. **Setup script:** pegá esto. Deja instaladas las dependencias en la imagen del entorno, que queda en caché unos 7 días:
   ```
   pip install -q --break-system-packages pandas==3.0.5 google-ads==33.0.0 google-api-python-client==2.200.0 \
     google-auth==2.58.0 google-auth-oauthlib==1.4.1 requests==2.34.2 openpyxl==3.1.5 PyYAML==6.0.3 \
     plotly==7.1.0 pillow==12.3.0 pymupdf==1.28.2 || true
   ```
6. **Who can use it:** dejalo personal. Si alguien más (Vicky, Felo) usa la cuenta, puede leer las variables.

## Renovar un acceso

El chequeo `python3 nube/chequear_accesos.py` (lo corre la tarea semanal todos los lunes) dice qué fuente falla y por
qué. Las variables del entorno se cambian en claude.ai/code → entorno «SEO-SEM» → Environment variables, desde
cualquier dispositivo; la sesión siguiente ya arranca con el valor nuevo.

- **Meta** (token vencido o revocado): en el Business Manager, usuario del sistema «marcomms-tablero» → generar
  token (permisos de `META_ADS.md`). Pegalo tal cual en la variable **`META_ACCESS_TOKEN`** (texto, sin base64): tiene
  prioridad sobre el de `SEOSEM_META_ADS`. No hace falta la compu.
- **Google (Search Console, GA4, Ads)** con `invalid_grant` (permiso vencido o revocado, o cambió el proyecto de
  Google Cloud): hay que reautorizar con `scripts/ads_auth.py --gsc|--ga4|--ads CUENTA`, que necesita un navegador y
  los archivos de acceso, en cualquier compu con el repo y Python (no tiene que quedar prendida). Después,
  `python nube/preparar_secretos.py` y reemplazar en el entorno las variables que cambiaron. No se hace en la nube:
  el token nuevo quedaría en la VM y la única forma de pasarlo al entorno sería mostrarlo en el chat.
- El proyecto de Google Cloud del cliente OAuth está en prueba gratuita y vence ~15 dic 2026 (gracia hasta ~14 ene
  2027): ver `docs/memoria/prueba-google-cloud.md`. Si se pasa a un proyecto nuevo, cambian `SEOSEM_CLIENT_SECRET`
  y los tres tokens de Google.

## Trabajo en la nube

- Lo que se genera en una sesión en la nube (datos nuevos, informes) queda en su rama `claude/…`. Para que llegue a la
  compu y al resto de las sesiones, hay que integrarlo a `main`: las tareas abren un PR y una persona lo aprueba
  (`nube/TAREAS.md`, «Al terminar»). Los commits que solo tocan `analisis/` no despliegan en Vercel.
- Antes de commitear datos, corré `python scripts/datos_gz.py comprimir`.
- Las sesiones hijas y los subagentes heredan este entorno: arrancan con el mismo hook y los mismos accesos.
- Para la entrega a MarComms-Reports, la sesión agrega ese repo con `add_repo` y `entrega_paid.py` encuentra el clon
  solo (en la compu sigue usando `_repos/paid-entrega`).
- Vercel no publica nada de `analisis/` (`.vercelignore`).
