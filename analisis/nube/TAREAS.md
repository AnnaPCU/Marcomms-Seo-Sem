# Tareas programadas en la nube

Desde el 26 nov 2026 las tareas recurrentes del proyecto corren como **tareas programadas de claude.ai en el entorno
«SEO-SEM»**, cada una en una sesión nueva. No dependen de que la compu de Felipe esté prendida ni de abrir la app de
escritorio. Cada tarea programada solo dice «seguí la sección X de `analisis/nube/TAREAS.md`»: lo que hace cada una
está acá y se cambia con un commit, sin tocar la tarea.

Horarios en hora de Argentina; el minuto está corrido unos minutos antes de la hora redonda a propósito (a la hora en
punto se encolan muchas tareas).

| Tarea | Cuándo | Qué hace | Sección |
|---|---|---|---|
| Chequeo semanal SEO-SEM | lunes 8:39 | accesos + gasto por día del mes en curso + cambios de Ads (vista Impacto) | [Semanal](#semanal) |
| Entrega Paid Media a MarComms-Reports | día 3, 6:43 | entrega del mes cerrado (Google Ads + Meta) | [Entrega Paid](#entrega-paid) |
| Cierre de mes SEO-SEM | día 4, 8:42 | `RUTINA_REVISION_MENSUAL_SEM.md` pasos 0–2 y 6 ter | [Cierre de mes](#cierre-de-mes) |
| Recomendaciones mensuales SEO-SEM | día 5, 8:58 | `RUTINA_REVISION_MENSUAL_SEM.md` pasos 3–7 | [Recomendaciones](#recomendaciones) |

Las tareas equivalentes de la app de escritorio («revision-mensual-sem», «recomendaciones-mensuales-sem»,
«entrega-paid-media-marcomms-reports», «impacto-semanal-sem») se desactivan en la compu para que no corran dos veces.

**Configuración que hace una persona en claude.ai** (no se puede desde una sesión):
- Las tareas se crearon el 26 nov 2026 desde una sesión, y esta organización no deja guardarles conectores desde ahí.
  En la pantalla de tareas programadas de claude.ai, sumale el **conector de Supabase** a «Chequeo semanal»,
  «Cierre de mes» y «Recomendaciones» (la entrega Paid no lo usa). Sin él, cargan nada: dejan los `.sql` y avisan.
- En el entorno «SEO-SEM» (Settings → Repositories), agregá **AnnaPCU/Marcomms-Seo-Sem**, para que cada sesión
  arranque con el repo, el hook y los permisos de `.claude/settings.json`. Mientras no esté, la tarea agrega el repo
  sola y corre el arranque a mano (lo dice el texto de cada tarea), pero sin esos permisos.

---

## Reglas comunes

**Al empezar**
1. Leé `analisis/CLAUDE.md` (marcas y límites de los datos) y `analisis/docs/memoria/INDICE.md`.
2. Desde `analisis/`: `python3 nube/chequear_accesos.py`. Si alguna fuente da **FALLA**, no extraigas nada de esa
   fuente ni cargues datos parciales. Terminá con un resumen que empiece con «FALLA DE ACCESO: <fuente> — <motivo>» y
   qué hay que renovar (sección «Renovar un acceso» de `nube/LEEME.md`). Nunca autorices cuentas vos.
3. Si la sesión no tiene el conector de Supabase, seguí igual: dejá los `.sql` en `analisis/informe/carga_<fecha>/` y
   en el resumen poné primero «Falta cargar: …» (como dice el paso 2 de la rutina).

**Durante**
- Google Ads, Search Console, GA4 y Meta son de **solo lectura**. Supabase solo con el SQL que generan
  `scripts/publicar.py` y `scripts/aplicar_revision.py`, verificado como dice la rutina (filas, sumas, md5).
- Nunca se muestran ni se copian tokens ni archivos de acceso (`client_secret.json`, `token*.json`, `google-ads.yaml`,
  `meta-ads.json`).
- No se toca el código del tablero (`src/`, `supabase/migrations/`, `public/`).

**Al terminar** (la VM se borra: lo que no se sube se pierde, incluido el histórico de Search Console)
1. Desde `analisis/`: `python3 scripts/datos_gz.py comprimir`.
2. `git add analisis/` y commit en la rama de la sesión (la `claude/…` que asigna la nube), solo con cambios dentro de
   `analisis/`. Si `git status` muestra algo fuera de `analisis/`, no lo commitees y anotalo en el resumen.
3. Push de esa rama y **un PR a `main`** titulado «<Tarea> · <período>» (p. ej. «Cierre de mes · 2026-11»), con el
   resumen en la descripción. **No se mergea**: lo aprueba una persona (se puede desde la app de GitHub en el celular).
   Los commits que solo tocan `analisis/` no disparan un deploy en Vercel (`ignoreCommand` de `vercel.json`).
4. Si aprendiste algo que vale para las próximas sesiones (un acceso, una decisión, un problema de datos), anotalo en
   el archivo que corresponda de `analisis/docs/memoria/` dentro del mismo PR.
5. El mensaje final es corto: qué se extrajo (hasta qué día por fuente), qué se cargó, el link del PR y cualquier
   falla. El detalle vive en el tablero y en el PR.

---

## Semanal

Mantiene al día el mes en curso en la vista «Día a día» y la vista «Impacto», y avisa con tiempo si un acceso venció
(antes del cierre de mes y de la entrega).

1. Reglas comunes, «Al empezar». Si Google Ads falla, terminá ahí.
2. Desde `analisis/scripts/`, con `D` = el 1 del mes en curso (si hoy es día 1 a 3, el 1 del mes anterior) y
   `H` = ayer:
   ```
   python3 ads_diario.py --desde <D> --hasta <H>
   python3 ads_cambios.py
   ```
3. Desde la raíz del repo, generá el SQL y cargalo con `execute_sql` (proyecto `cogdfbonpvvuzhurmvlq`):
   ```
   python3 scripts/publicar.py --sql analisis/informe/carga_semanal/dia.sql     --solo dia --desde-fecha <D>
   python3 scripts/publicar.py --sql analisis/informe/carga_semanal/cambios.sql --solo cambios
   ```
   Mandá el texto tal cual sale del archivo (el de cambios en tandas de ~15 KB) y verificá como en el paso 2 de
   `RUTINA_REVISION_MENSUAL_SEM.md`: filas y suma de coste/clics por día de `metricas_dia` desde `D` contra
   `informe/datos_gasto_diario.json`, y cantidad + md5 de `cambios_ads` contra `informe/datos_cambios_ads.json`.
4. Reglas comunes, «Al terminar». Los `.sql` de `informe/carga_semanal/` no se commitean (se regeneran): borralos
   antes del commit.

## Entrega Paid

Contrato: `docs/ENTREGA_PAID_DESDE_SEO_SEM.md` del repo AnnaPCU/MarComms-Reports. Detalle en
`analisis/docs/memoria/entrega-paid-marcomms-reports.md`.

1. Reglas comunes, «Al empezar». Si fallan Google Ads o Meta, no entregues nada.
2. Agregá AnnaPCU/MarComms-Reports a la sesión con permiso de push (herramienta `add_repo`, `access: "push"`) y
   clonalo donde indique (normalmente `/home/user/marcomms-reports`). `entrega_paid.py` encuentra ese clon solo.
3. Desde `analisis/scripts/`: `python3 entrega_paid.py` (mes anterior, valida con el tooling de allá y **no** sube).
   Si dice «Nada nuevo para entregar» o algo no valida, terminá con el resumen.
4. Si validó todo: `python3 entrega_paid.py --push`. Esta tarea está autorizada a pushear a `main` de MarComms-Reports
   **solo** a través de este script, que commitea únicamente `metricas/paid-media/`.
5. Reglas comunes, «Al terminar» (normalmente no hay cambios en este repo; si no hay, no abras PR).

## Cierre de mes

1. Reglas comunes, «Al empezar».
2. Seguí `analisis/RUTINA_REVISION_MENSUAL_SEM.md`, pasos 0, 1, 2 y 6 ter (datos e impacto; **sin tocar tarjetas**).
   En la nube no existe `analisis/supabase-service.json`: la carga va siempre por el conector (bloque «Si no existe»).
3. Reglas comunes, «Al terminar». PR «Cierre de mes · <M>».

## Recomendaciones

1. Reglas comunes, «Al empezar».
2. Si el PR «Cierre de mes · <M>» todavía no está en `main`, traé sus datos antes de analizar:
   `git fetch origin <rama del PR> && git merge --no-edit FETCH_HEAD` (la rama figura en el PR; buscalo con
   `list_pull_requests`). Si no hay PR del cierre o los datos de `M` no están cargados, hacé antes los pasos 1 y 2 de
   la rutina.
3. Seguí `analisis/RUTINA_REVISION_MENSUAL_SEM.md`, pasos 3 a 7.
4. Reglas comunes, «Al terminar». PR «Recomendaciones · <R>».

---

## Permisos para que las tareas no se frenen

Una sesión sin nadie mirando se queda esperando en el primer permiso que pida (pasó el 3 nov 2026). Las reglas de
permiso del repo las agrega una persona, no Claude: copiá esto dentro de `.claude/settings.json` (al mismo nivel que
`"hooks"`) y commitealo. Valen también en la compu.

```json
"permissions": {
  "allow": [
    "Bash(python3 *)", "Bash(python *)", "Bash(cd *)", "Bash(ls *)",
    "Bash(git status*)", "Bash(git diff*)", "Bash(git log*)", "Bash(git fetch *)", "Bash(git merge *)",
    "Bash(git add analisis/*)", "Bash(git commit *)", "Bash(git push -u origin claude/*)",
    "Bash(git clone *)", "Bash(GIT_LFS_SKIP_SMUDGE=1 git clone *)",
    "mcp__Supabase__execute_sql", "mcp__Supabase__list_tables",
    "mcp__github__create_pull_request", "mcp__github__list_pull_requests", "mcp__github__pull_request_read",
    "mcp__claude-code-remote__add_repo"
  ],
  "deny": [
    "Bash(git push --force*)", "Bash(git push -f*)", "Bash(git push * --force*)", "Bash(git push * main*)",
    "Read(analisis/client_secret*.json)", "Read(analisis/token*.json)", "Read(analisis/google-ads.yaml)",
    "Read(analisis/meta-ads.json)", "Read(analisis/supabase-service.json)"
  ]
}
```

`Bash(python3 *)` deja correr cualquier Python sin preguntar: hace falta porque el análisis del paso 4 de la rutina se
calcula con scripts propios sobre los CSV. Los `deny` impiden forzar un push, pushear a `main` desde Bash y leer los
archivos de acceso con la herramienta de lectura.
