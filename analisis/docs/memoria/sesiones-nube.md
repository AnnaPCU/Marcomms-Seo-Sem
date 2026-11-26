---
name: sesiones-nube
description: Entorno de nube «SEO-SEM» probado de punta a punta el 26 nov 2026; tareas programadas en la nube con PR a main; qué sigue dependiendo de una persona
metadata:
  type: project
---
**Prueba (26 nov 2026):** sesión nueva en el entorno «SEO-SEM» con todo andando solo. El hook instaló nada (el setup
script ya dejó las dependencias), descomprimió los 6 CSV y armó los 5 archivos de acceso. Accesos OK: Google Ads
(1606422184, ARS), Search Console (argentina.controlunion.com: 150 clics / 13.149 impresiones del 18 al 24 nov), GA4
(512118948: 596 sesiones del 19 al 25 nov), Meta (2 cuentas) y Supabase por el conector (74 campañas). Sin bloqueos de
red. `entrega_paid.py --mes 2026-10 --forzar --sin-meta` regeneró octubre en un clon común de MarComms-Reports y validó
(43 campañas, ARS 4.040.805,59, igual que lo entregado).

**Decisiones (26 nov 2026, pedido de Anna):** que todo pueda correr sin la compu de Felipe prendida.
- Las tareas recurrentes pasan a tareas programadas de claude.ai en el entorno «SEO-SEM» (`nube/TAREAS.md`): semanal
  (lunes), entrega Paid (día 3), cierre de mes (día 4), recomendaciones (día 5). Cada una abre un PR a `main` con lo
  que genera; no se mergea sola.
- `vercel.json` tiene `ignoreCommand`: los commits que solo tocan `analisis/` no despliegan.
- La VM está en UTC: `nube/sesion.sh` fija `TZ=America/Argentina/Buenos_Aires` con `CLAUDE_ENV_FILE`.
- `nube/chequear_accesos.py` prueba las 4 fuentes sin reescribir tokens; las tareas lo corren primero.
- `ads_export.py --test` ya no escribe en `datos/ads/api/log_ads_*.jsonl` (es un archivo del repo).
- Supabase en la nube solo por el conector (SQL de `publicar.py --sql`); `SEOSEM_SUPABASE_SERVICE` no hace falta.
- Meta se puede renovar sin la compu con la variable `META_ACCESS_TOKEN` (texto); Google no: la reautorización
  necesita un navegador y una compu cualquiera con el repo (ver «Renovar un acceso» en `nube/LEEME.md`).

**Lo que hace una persona, no Claude:**
- Aprobar los PR de las tareas.
- Las reglas de permiso de `.claude/settings.json` (el clasificador no deja que Claude se las agregue): bloque listo en
  `nube/TAREAS.md`, «Permisos».
- Desactivar en la app de escritorio las tareas viejas para que no corran dos veces.
- Google Cloud: el proyecto vence ~15 dic 2026 ([[prueba-google-cloud]]). Meta: regenerar el token que se pegó en el
  chat el 10 nov ([[integracion-meta-ads]]).
Ver [[mapa-del-proyecto]], [[marcomms-seo-sem-dashboard]], [[entrega-paid-marcomms-reports]].
