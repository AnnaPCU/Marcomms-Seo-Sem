# Proyecto SEO-SEM en sesiones en la nube

El proyecto de análisis vive en `analisis/` del repo AnnaPCU/Marcomms-Seo-Sem. Así se puede abrir como sesión en la
nube (claude.ai/code), igual que MarComms Hub, sin depender de que la compu de Felipe esté prendida.

## Cómo funciona

- **Código y datos:** vienen con el repo.
  - Los CSV de más de 5 MB viajan comprimidos (`.csv.gz`); ver `scripts/datos_gz.py`.
  - Al arrancar cada sesión, `nube/sesion.sh` (hook SessionStart de `.claude/settings.json`) hace tres cosas: instala las dependencias si faltan, descomprime los CSV y arma los archivos de acceso.
- **Accesos de Google y Meta:** salen de variables del entorno de nube «SEO-SEM» (`SEOSEM_*`, cada una en base64). `nube/credenciales.py` los escribe en la VM; nunca van al repo.
- **Supabase:** por el conector de claude.ai (no necesita permiso de red). Para la carga por REST de `scripts/publicar.py` hace falta además `SEOSEM_SUPABASE_SERVICE` y el dominio `*.supabase.co`.
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

## Cuándo hay que volver a cargar una variable

- Si se renueva un acceso en la compu (por ejemplo con `scripts/ads_auth.py`), corré otra vez el paso 1 y reemplazá esa variable en el entorno.
- Si el proyecto de Google Cloud del cliente OAuth vence o cambia (ver `docs/memoria/prueba-google-cloud.md`), dejan de andar los accesos de Google en la compu y en la nube por igual.

## Trabajo en la nube

- Lo que se genera en una sesión en la nube (datos nuevos, informes) queda en su rama `claude/…`. Para que llegue a la compu y al resto de las sesiones, hay que integrarlo a `main` (PR o merge).
- Antes de commitear datos, corré `python scripts/datos_gz.py comprimir`.
- Vercel no publica nada de `analisis/` (`.vercelignore`).
