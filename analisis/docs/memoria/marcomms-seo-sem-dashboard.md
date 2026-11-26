---
name: marcomms-seo-sem-dashboard
description: "Estado y decisiones del tablero web \"Marcomms SEO-SEM\" (repo, Supabase, Vercel, identidad MarComms, loader mensual)"
metadata:
  node_type: memory
  type: project
  originSessionId: 3f17a333-cb57-48e9-99be-02fbe458983e
  modified: 2026-11-10T21:50:48.553Z
---

Tablero Kanban de recomendaciones SEM/SEO. Repo local `Documentos\Marcomms SEO-SEM\`, GitHub privado
`AnnaPCU/marcomms-seo-sem` (rama única `main`, creado 28 sep 2026 con el token guardado en git credential).
Identidad MarComms (navy #1b1e42, azul #009ceb, logos en `public/marca/`); CU y PS aparecen solo como chips de texto.
Stack: Vite 8 + React 19 + TS + Tailwind 3 + Supabase + dnd-kit; `npm run verificar` antes de cada push.
Datos entran por `scripts/publicar.py` (env SUPABASE_URL + SUPABASE_SERVICE_KEY) desde
`proyecto/informe/recomendaciones.json`, que genera `proyecto/scripts/exportar_recomendaciones.py AAAA-MM`
(90 recomendaciones en sep 2026: 28 plan, 24 anuncios, 38 SEO; clave estable marca:tipo:campaña|sitio:slug).

**Decisión 29 sep 2026:** la base vive en el esquema `seo_sem` del proyecto "MarComms Hub Project"
(`cogdfbonpvvuzhurmvlq`, org marcomms-hub, URL https://cogdfbonpvvuzhurmvlq.supabase.co) porque el plan gratuito
de Supabase limita a 2 proyectos activos por usuario en todas sus orgs (AnnaPCU tiene otro en otra org). Migración
aplicada, esquema expuesto por REST (`alter role authenticator set pgrst.db_schemas`), RLS por dominio en políticas
(no trigger en auth.users), seed de septiembre cargado por MCP execute_sql (42 campañas, 131 grupos, 90 tarjetas,
42 métricas). Vercel: proyecto `marcomms-seo-sem` (prj_bp9H9xgo4tzK0juLg6vyDpC2JcBO) creado por Felipe, en
producción en https://marcomms-seo-sem.vercel.app; la integración de Claude no tiene acceso a ese proyecto
(404/403), Felipe cargó las env vars a mano. El repo se renombró a `AnnaPCU/Marcomms-Seo-Sem`. Pendiente usuario:
agregar la URL de Vercel + http://localhost:5174 en Supabase Auth → URL Configuration → Redirect URLs; Google
provider sin configurar (magic link funciona). Vista de gasto: columna «Presupuesto» (presupuesto diario de la
cuenta × días con datos en la vista mensual) a la izquierda del gasto, rojo si gasta >5% por encima.
Gasto: `analisis_gasto.py` usa el reporte `anuncios` (gasto completo); el de `terminos` solo muestra ~53%. Luego: crear proyecto Supabase "Marcomms SEO-SEM" en sa-east-1,
aplicar `supabase/migrations/0001_esquema.sql`, configurar Google en Auth, cargar env en Vercel, correr publicar.py.

**2 oct 2026:** vista «Día a día» en Presupuesto (calendario + detalle del día + grilla campaña × día) sobre
`seo_sem.metricas_dia` (migración 0004 aplicada). Carga: `proyecto/scripts/ads_diario.py` → `informe/datos_gasto_diario.json`
→ `publicar.py --sql … --solo dia` → MCP execute_sql. PCU se muestra como «Peterson Control Union (ISO)». Accesos (5 oct 2026):
Google Ads con tmpcugroup@gmail.com, Search Console con tmisrahi@onepeterson.com; `scripts/ads_auth.py --ads|--gsc CUENTA`
sin abrir el navegador solo (pasarle el link a Felipe; el navegador predeterminado entra con otra cuenta). El proyecto de Cloud
está en la org personal «tmisrahi-org»: «Interno» bloquea a onepeterson. Desde el 6 oct 2026 la app está «Externa · En producción»: los permisos ya no vencen a los 7 días (Google no informa refresh_token_expires_in).

**Ojo, esquema expuesto (2 nov 2026):** el proyecto Supabase es compartido con el Hub. El 27 oct otra sesión expuso `content_creator` desde el panel y la lista quedó «public, graphql_public, content_creator»: `seo_sem` desapareció y todo el tablero dio 406 (PGRST106). Ya no existe el `pgrst.db_schemas` en el rol authenticator. La lista correcta es `public, graphql_public, content_creator, seo_sem` (Project Settings › Data API › Exposed schemas). Cambiar esa config desde execute_sql lo bloqueó el clasificador: lo hace el usuario en el panel. Si vuelve a aparecer el error, el tablero ahora lo dice con texto (commit 5a44d61).

**Cierre de mes automático (10 nov 2026):** la tarea «revision-mensual-sem» (ahora «Cierre de mes…», día 4 a las 9:00) extrae el mes cerrado con `--hasta <último día>`, lo carga con `publicar.py --desde-mes M` (y `--desde-fecha` para días) y revisa SEM **y SEO** (`aplicar_revision.py` acepta nuevas `:SEO:` con ficha seo). La corrida del 3 nov falló: sin conector de Supabase y colgada en un permiso de Bash; se pidió al usuario «Run now» una vez para guardar las aprobaciones. El tablero marca «incompleto» un mes terminado con datos parciales y muestra las campañas activas sin gasto (commit efdf08d); mover tarjetas refresca por detrás sin loader. Octubre 2026 cargado completo y verificado (ARS 4.040.806, 43 campañas; GA4 11.147 sesiones).

**Vista «Impacto» (10 nov 2026, commit 95c9b66):** ruta /impacto. Tabla `seo_sem.cambios_ads` (migración 0007) con el historial change_event de Ads (`proyecto/scripts/ads_cambios.py`, Google guarda 30 días; activaciones de anuncios se completan con sus textos actuales) → `publicar.py --solo cambios`. `src/utils/impacto.ts` cruza cada ítem de las «hechas» con esos cambios (aplicado / no se ve / a criterio) y compara 28 días antes del primer cambio vs. después del último (mín. 14 días; si no, «midiendo»). Cargados 192 cambios (campañas con hechas, desde 18 oct, md5 verificado) y gasto diario 1–8 nov (9 nov parcial, sin cargar). Cargas grandes: el SQL de cambios pesa >100 KB, va en tandas de ~15 KB; los resultados grandes de execute_sql quedan en un archivo de tool-results que se puede leer con Python. `publicar.py` acepta `proyecto/supabase-service.json` para REST (pendiente que el usuario lo cree). La tarea semanal «impacto-semanal-sem» (lunes) la bloqueó el clasificador: falta que el usuario la apruebe.

**Limpieza (10 nov 2026, commit 86eed53):** sin Excel (BotonExportar/exportar.ts borrados), sin tipo de mejora (filtro, chips y `accion` en filtros), sin intros en SEM/SEO, Historial fuera del menú y rutas (archivo `routes/Historial.tsx` queda). Impacto: país en chips + optimizaciones de a una con flechas, solo resultado (5 indicadores antes → después); mínimo 14 días después del cambio; sin ninguna medida muestra «Próximamente» con la fecha del primer resultado (13 nov para las de Portugal).

**Presupuesto (12 nov 2026, commit 96f35e5):** por defecto el mes actual, armado desde metricas_dia (`mesDesdeDiario`) mientras no tiene fila mensual; meses como botones (4 recientes + «Anteriores…»). Modos: Mes · Cada 10 días (`VistaDecenas`, tramos 1–10/11–20/21–fin contra presupuesto diario × días con datos + % del mes consumido) · Día a día; «Promedio por día» eliminado a pedido. El badge del header toma la fecha más nueva entre la extracción de cierre y el último día de metricas_dia. Gasto diario cargado hasta el 11 nov. Para que el mes en curso no se congele hace falta una carga diaria/semanal de metricas_dia (pendiente de aprobar).

**Why:** el usuario quiere un solo lugar para seguir mes a mes qué mejora se aplicó; ver [[felipe-perfil]].
**How to apply:** no crear un segundo repo ni otro proyecto Supabase; retomar desde los bloqueos listados.

**GA4 (9 oct 2026):** pestaña «Sitios · GA4» en producción (commit 271f77e). Tabla `seo_sem.ga4_sitio_mes`; flujo mensual: `proyecto/scripts/ga4_export.py` → `informe/datos_ga4.json` → `publicar.py --solo ga4`. Contactos reales = form_submit gform_ + click_email fuera de empleo/academia/reclamos; HubSpot iframe no llega a GA4. Pendiente avisar/corregir: `reporte_trimestral.py` (otra sesión) cuenta click_email + form_submit crudos como conversiones (inflado por /exp-admin, buscador y vacantes).

**Histórico (19 oct 2026, commit a276763):** Ads cargado feb–oct 2026 desde dos cuentas: actual 1606422184 «Control Union - (en ARG)» (ARS, desde jul 2026) y anterior 6527967282 «Peterson Technologies» (EUR, login_customer_id = la misma cuenta; registrada en google-ads.cuentas.json → historicas). Felipe eligió pasar todo a pesos: promedio mensual BCRA (API estadisticascambiarias). `ads_historico.py` → `publicar.py --solo historico`; `ga4_export.py 2025-12 2026-10` (GA4 arranca dic 2025). Período por defecto = último mes cerrado (a Felipe le gusta así). Cargas grandes por MCP: copiar en tandas chicas y verificar con md5 contra el JSON local (una vez se corrompió una fila al transcribir).

**Revisión mensual SEM (desde 21 oct 2026):** tarea programada «revision-mensual-sem» (día 3 de cada mes, 9:00) que sigue `proyecto/RUTINA_REVISION_MENSUAL_SEM.md` y aplica cambios con `proyecto/scripts/aplicar_revision.py` (JSON → SQL; solo toca tarjetas en «propuesta», verifica «hechas», registra el movimiento en el historial con usuario «Revisión mensual (Claude)»). **Exportar a Excel** en SEM y SEO (commit a7ef067): hojas Tareas (todos los campos + evidencia en columnas + JSON), Historial y Léeme.

**Modo oscuro y estado persistente (21 oct 2026, commit 17ef0d3):** colores = variables CSS en `src/index.css` (`:root` claro / `.dark` oscuro); usar `bg-mc-sup` para superficies (no `bg-white`) y `bg-mc-fuerte` para rellenos oscuros (no `bg-mc-navy`). Estado de vistas con `usePersistente` (localStorage, prefijo `mc-seo-sem:`). Cambios en `tailwind.config.js` no los toma un `npm run dev` ya abierto: probar con la config «marcomms-preview-build» (vite preview en :4181, en `.claude/launch.json` de Optimizaciónes SEO-SEM) o reiniciar el dev server.

**Ficha «campana» (22 oct 2026, commit 6435a85):** formato nuevo de tarjeta SEM (`src/components/tablero/FichaCampana.tsx`): una tarjeta por acción y por campaña, con dónde (campaña, grupo, id de anuncio), por qué, lo ya hecho, pasos, keywords y negativas con motivo + `negativas_decision`, y por anuncio cada propuesta con motivo, `reemplaza` y `prioritario` (destacada). `publicar.py` no pisa tarjetas con `ficha = 'campana'`. 10 tarjetas reescritas y 9 de plan descartadas por unificación (`proyecto/scripts/unificar_tarjetas_sem.py` → `informe/unificacion_sem_2026-10.sql/json`); cada una verificada por md5 de `evidencia::text` contra el JSON local (script de serialización tipo jsonb: claves ordenadas por largo y luego bytes). Reglas: [[reglas-tarjetas-sem]].

**Tarjetas concretas (28 oct 2026, commits 2908e61 y b79ea70):** cada paso lleva `items` (qué cargar literal, con botón Copiar) y hay ficha `seo` (sitio + páginas, acciones `contenido`/`tecnico`). Todas las tarjetas SEM y SEO abiertas pasaron a ese formato: 29 SEM campana en propuesta + 4 en proceso, 33 SEO en propuesta, verificadas por md5. Flujo: `informe/concretar_2026-10/BRIEF.md` (brief para agentes) → lotes JSON → `scripts/chequear_lote.py` (valida con `validar_campana`/`validar_seo` de `aplicar_revision.py`) → `scripts/cargar_lotes.py <out> <lotes>` (un SQL por tarjeta + md5.txt) → MCP execute_sql. Vista previa sin contraseña: script Playwright que intercepta Supabase con fixtures (`prueba_concretar.py` en el scratchpad de la sesión) contra vite preview :4181.
