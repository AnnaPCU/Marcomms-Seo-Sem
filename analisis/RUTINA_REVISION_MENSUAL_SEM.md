# Rutina mensual — cierre de mes del tablero (datos, SEM y SEO)

Pedido de Felipe (21 oct 2026): todos los meses, apenas esté completa la data del mes anterior, revisar si conviene
sumar optimizaciones nuevas en «SEM · campañas» del tablero Marcomms SEO-SEM, y revisar las actuales: ajustar o
descartar las que ya no tengan sentido. Ampliado el 10 nov 2026: que sea **automático y completo** — extraer el mes
cerrado, cargarlo al tablero y revisar **SEM y SEO** sin que nadie lo pida. Un mes nunca se muestra como cerrado con
datos parciales (en oct 2026 el tablero mostró octubre con datos hasta el 18 porque nadie volvió a extraer).

La corre una tarea programada el **día 4 de cada mes a las 9:00** (desde el 26 nov 2026, en la nube: ver
`nube/TAREAS.md`): Google Ads consolida el mes en unas 48 horas y
Search Console publica los datos finales con 2 o 3 días de atraso, así que el día 4 ya está el último día del mes en
las tres fuentes. Si se corre a mano, seguir los mismos pasos.

Desde el 17 nov 2026 son **dos tareas**: el **día 4** «revision-mensual-sem» hace los pasos 0–2 y 6 ter (datos y
impacto, sin tocar tarjetas) y el **día 5** «recomendaciones-mensuales-sem» hace los pasos 3–7 (recomendaciones nuevas
y actualización de las «propuesta» y «en proceso» con todo el histórico + el mes cerrado). Si el día 5 los datos de
`M` no están cargados, esa tarea hace antes los pasos 1 y 2.

Antes de empezar, leé `analisis/CLAUDE.md` completo (marcas, accesos, reglas de los cruces y límites de los datos).

---

## 0. Definiciones del mes

- **Mes analizado** (`M`): el mes calendario anterior. **Mes de la revisión** (`R`): el actual; es el `mes_alta` de
  las tarjetas nuevas.
- Comparación: `M` contra el mes anterior a `M` (`M-1`).
- Todo el gasto en pesos (la cuenta anterior, en euros, ya está convertida en el histórico).

## 1. Actualizar los datos (solo lectura)

Desde `analisis/scripts/`:

```
python ads_estructura.py                                                # catálogo actual: campañas, grupos, keywords, negativos, anuncios
python ads_export.py --desde <1 de M> --hasta <último de M>             # términos, keywords (QS), anuncios y recursos de M
python analisis_gasto.py --desde <1 de M> --hasta <último de M>         # gasto de M por campaña
python ads_diario.py --desde <1 de M-1> --hasta <último de M>           # gasto por día (M-1 y M)
python ads_cambios.py                                                   # historial de cambios de Ads, últimos 29 días (vista Impacto)
python ads_historico.py --hasta <último de M>                           # mes a mes por campaña y grupo, con M cerrado
python ga4_export.py <M-1> <M>                                          # GA4 de M-1 y M completos
python gsc_historico.py                                                 # Search Console (orgánico) hasta el último día final
```

`ads_cambios.py` es la excepción: Google guarda el historial de cambios solo 30 días y la carga es idempotente, así
que siempre va hasta hoy. Todo lo demás con `--hasta <último de M>`: el mes en curso (`R`) no se extrae ni se carga, para no mezclar un mes cerrado con
uno parcial. **Control de mes completo** (si alguno falla, **no sigas**: dejá anotado el problema en el resumen):
- `informe/datos_ads_historico.json`: todas las filas del mes `M` con `hasta` = último día de M.
- `informe/datos_ga4.json`: los sitios del mes `M` con `hasta` = último día de M.
- `datos/gsc-historico/*/gsc_*_hist_daily.csv`: la fecha más nueva ≥ último día de M (si todavía no, Search Console
  no publicó el final: anotalo y seguí solo con Ads y GA4).
- Si un token venció (Ads: `ads_auth.py --ads tmpcugroup@gmail.com`; GSC/GA4: `ads_auth.py --gsc|--ga4
  tmisrahi@onepeterson.com`), no autorices cuentas vos: frená y reportalo.

## 2. Cargar los datos al tablero

Proyecto Supabase `cogdfbonpvvuzhurmvlq`, esquema `seo_sem`.

**Si existe `analisis/supabase-service.json`** (solo en la compu; en la nube no existe y se usa el conector. Clave de servicio local, como `meta-ads.json`; nunca se lee en voz alta
ni se copia a otro lado), cargá directo por REST, sin pasar SQL por el conector:

```
cd ../..                     # raíz del repo (scripts/publicar.py)
python scripts/publicar.py --solo dia --desde-mes <M>
python scripts/publicar.py --solo cambios
python scripts/publicar.py --solo ga4 --desde-mes <M>
python scripts/publicar.py --solo extracciones
```

Campañas e histórico (`--solo campanas`, `--solo historico`) van siempre en modo `--sql` por el conector, como en el
bloque de abajo: cruzan las dos cuentas de Ads por `ads_id` y el modo REST no lo hace.

**Si no existe**, por el conector:

```
cd ../..                     # raíz del repo (scripts/publicar.py)
python scripts/publicar.py --sql <carpeta>/campanas.sql     --solo campanas
python scripts/publicar.py --sql <carpeta>/historico.sql    --solo historico --desde-mes <M>
python scripts/publicar.py --sql <carpeta>/dia.sql          --solo dia       --desde-mes <M>
python scripts/publicar.py --sql <carpeta>/ga4.sql          --solo ga4       --desde-mes <M>
python scripts/publicar.py --sql <carpeta>/cambios.sql      --solo cambios
python scripts/publicar.py --sql <carpeta>/extracciones.sql --solo extracciones
```

`--desde-mes` deja solo lo del mes cerrado (el histórico anterior ya está en la base y no cambia): cada archivo queda
en unas decenas de KB. Ejecutá cada archivo con `execute_sql`, sentencia por sentencia si son largas. **No
transcribas datos a mano**: mandá el texto tal cual sale del archivo y después verificá contra el JSON local (filas y
suma de coste/clics de M en `metricas_mes`, `metricas_grupo_mes` y `metricas_dia`, que tienen que dar lo mismo; para
GA4, sesiones por sitio de M; para los cambios, cantidad de filas y md5 de `string_agg(substr(evento_id, 35) || resumen,
'|' order by evento_id collate "C")` contra el mismo cálculo en Python sobre `informe/datos_cambios_ads.json`). Si algo
no cuadra, corregilo antes de seguir. El SQL de cambios puede pesar >100 KB: mandalo en tandas de ~15 KB.

**Si la sesión no tiene el conector de Supabase** (pasó el 3 nov 2026): no te quedes esperando. Dejá los `.sql` en
`analisis/informe/carga_<R>/`, seguí con el análisis y escribí la revisión igual (paso 6, sin ejecutar), y en el
resumen poné primero «Falta cargar: correr los .sql de informe/carga_<R>/ y revision_*_<R>.sql».

## 3. Leer el tablero actual

```sql
select r.clave, r.marca, r.estado, r.prioridad, r.titulo, r.detalle, r.evidencia, r.mes_alta, r.motivo_descarte,
       r.verificada_api, c.nombre as campana, g.nombre as grupo
from seo_sem.recomendaciones r
left join seo_sem.campanas c on c.id = r.campana_id
left join seo_sem.grupos g on g.id = r.grupo_id
where r.tipo = 'SEM' order by r.marca, c.nombre;
```

## 4. Analizar el mes (con todo el histórico)

Felipe (17 nov 2026): cada mes nuevo, recomendaciones nuevas o actualizadas, sacadas de **todo el histórico + lo que
pasó en el último mes**, y solo cuando tienen sentido. No alcanza con `M` contra `M-1`:

- **Histórico**: `seo_sem.metricas_mes` / `metricas_grupo_mes` (desde el primer mes cargado), los CSV mensuales de
  `datos/ads/api/` y Search Console de 16 meses. Sirve para separar tendencia de ruido (un mes malo aislado no es una
  tarjeta; tres meses cayendo sí), estacionalidad y lo que ya se probó.
- **Último mes (`M`)**: lo que cambió de verdad: términos nuevos, gasto, CTR, CPC, conversiones, nivel de calidad.
- **Impacto** de lo ya hecho (`seo_sem.cambios_ads` y §6 ter): no repetir algo que se aplicó y no funcionó; si
  funcionó, ver si se puede extender a campañas parecidas.
- **Sin evidencia, no hay tarjeta.** Si un mes no trae nada nuevo que valga la pena, se dice en el resumen y listo.

Por cliente → país → campaña → grupo:

- **Gasto y presupuesto**: campañas limitadas por presupuesto (≥95% del diario), con presupuesto ocioso (<50%),
  activas sin gasto, pausadas o eliminadas.
- **Eficiencia**: CTR, CPC, conversiones y costo por conversión (con pocas conversiones no hay base estadística:
  decidí por relevancia de intención, como dice CLAUDE.md §10).
- **Términos de búsqueda** (`ads_*_terminos_*`): términos nuevos sin relación con el servicio → negativas
  (usá las listas de `analisis_reglas.py` como referencia); términos relevantes con clics que no son keyword →
  keywords. Antes de negativizar un tema, comprobá que el sitio no rankee para él (CLAUDE.md §6.6).
- **Keywords** (`ads_*_keywords_*`): nivel de calidad y sus componentes; concordancias.
- **Anuncios** (`ads_*_anuncios_*`, `ads_*_recursos_*`): recursos con calificación baja, títulos que no nombran la
  norma, URL final que no coincide con la página que rankea en orgánico.
- **Landing** (GA4, tabla `ga4_sitio_mes`): páginas pagas con poca interacción, visitas pagas sin contactos.
- **Orgánico** (Search Console): canibalización (pago donde ya se está 1–3 orgánico) y zona 8–20 donde el pago
  rinde. Coincidencia por **tema**, nunca por string exacto.

Los scripts `analisis_estado.py`, `analisis_gasto.py` y `analisis_anuncios.py` sirven de base (leé su encabezado);
si un script está atado a ventanas viejas, calculá directo desde los CSV.

## 5. Decidir tarjeta por tarjeta

| Situación | Qué hacer |
|---|---|
| **Propuesta** que sigue vigente | Dejarla, o **ajustarla** si cambiaron los números, la prioridad o la propuesta. |
| **Propuesta** que ya no tiene sentido (se resolvió sola, la campaña se pausó o eliminó, los datos la contradicen) | **Descartarla** con un motivo concreto y con datos («En oct el término X no volvió a aparecer: 0 clics»). |
| **En proceso** | **Actualizarla si los datos nuevos cambian algo** (en `ajustes`, igual que una propuesta): pasos o ítems que ya no aplican, nuevos términos para negativizar, otra prioridad. No se cambia de columna ni se reescribe lo que el equipo ya aplicó: se suma o corrige lo pendiente. El `motivo` dice **qué cambió y por qué**, en una línea con datos (el tablero la muestra como «Actualizada» con ese texto hasta la revisión siguiente). Si quedó obsoleta, no se descarta: se anota en el resumen. |
| **Hecha** | Comprobar en la estructura/API si se aplicó (negativa cargada, keyword creada, anuncio cambiado). Si se confirma, **verificarla**. |
| Oportunidad nueva con evidencia | **Tarjeta nueva**, solo si no existe ya una sobre la misma campaña y tema (en ese caso, ajustar esa). |

Reglas de Felipe para las tarjetas (21 oct 2026, no negociables):

1. **Una acción, una tarjeta.** No repartir una misma recomendación en dos o más tarjetas (p. ej. «grupo nuevo» en una y
   «anuncio del grupo» en otra). Lo normal es **una tarjeta abierta por campaña** con todo lo que hay que hacer ahí, en
   pasos. Antes de crear una, buscá si la campaña ya tiene una tarjeta abierta: si la tiene, **ajustá esa** (sección
   `ajustes`) en vez de crear otra. Una acción que abarca varias campañas (p. ej. pausar dos) va en una sola tarjeta
   que las nombra a todas en `evidencia.campanas`.
2. **Siempre dónde.** Nombre completo de la campaña (como figura en Google Ads), y si la mejora toca un grupo o un
   anuncio, cuál: nombre del grupo e **id del anuncio** (del snapshot de estructura). Si el grupo tiene varios anuncios,
   decí en cuál y por qué.
3. **Grupo nuevo → keywords y negativas.** Toda propuesta de grupo nuevo trae las keywords recomendadas (texto,
   concordancia, motivo) y una decisión explícita sobre negativas (`negativas_decision`: si hay que agregar, cuáles y por
   qué, o por qué no hace falta).
4. **Ajuste de anuncio → el porqué.** El motivo del cambio (`motivo` del anuncio, con datos) y, por cada título y
   descripción propuestos, su motivo y a cuál reemplaza. Marcá con `prioritario: true` las que de verdad conviene hacer
   (se ven destacadas en el tablero); el resto son variantes. Lo que se quita se copia **exacto** del anuncio vigente
   (`titulos_hoy` / `descripciones_hoy` del snapshot), y el anuncio no puede quedar con más de 15 títulos ni 4
   descripciones: si ya está lleno, cada propuesta reemplaza a uno. El validador lo comprueba.
6. **Cada paso dice exactamente qué cargar** (Felipe, 28 oct 2026: «no entiendo qué negativa poner, qué exactas poner»).
   Todo paso de negativas, keywords, pausa, anuncio o estructura lleva `items`: cada negativa y keyword con su
   concordancia y su destino (toda la campaña / grupo «X»), cada título y descripción con el texto que reemplaza, cada
   grupo nuevo con su URL. Nada de «las de la tabla», «de abajo», «Anexo», «negativos de marcas», «pausar el resto».
   Si hay un número (tope de CPC, presupuesto), se da el número. Cambiar la concordancia = agregar la nueva + pausar la
   vieja. Formato de `items` y ejemplo real: `informe/concretar_2026-10/BRIEF.md` y la tarjeta de ISCC en
   `informe/unificacion_sem_2026-10.json`. El validador rechaza un paso sin `items` o con esas remisiones.
7. **Fecha de los datos.** `datos_hasta` con el día de la estructura/reportes usados; si un dato viene de un análisis
   anterior, decí de cuándo es.
8. **Al grano** (Felipe, 10 nov 2026: «planteame el problema, la solución, listo»). El tablero muestra: dónde, **el
   problema** (`detalle` de la tarjeta: 2 o 3 frases con el dato que duele) y **la solución** (`evidencia.resumen`:
   una línea), y después **qué hacer, en orden** (`pasos` con sus `items`). Si hay que arrancar por una campaña o un
   anuncio y después seguir con otro, va en pasos separados, cada uno con su `donde`. `por_que` y `ya_hecho` quedan
   plegados como respaldo: cortos. Las tablas de `keywords`, `negativas` y `anuncios` no se muestran (los pasos ya
   dicen qué cargar), pero se siguen completando para el Excel y el validador.
9. **CUC USA** (pedido del cliente, 10 nov 2026): todo lo de Control Union en Estados Unidos se llama «CUC USA» en
   títulos, detalle, resumen y textos (`unidad: "CUC USA"`). Los nombres reales de campaña se citan tal cual figuran
   en Google Ads («CU United States - …») mientras no los renombren.
10. **«Hecha» no es «todo hecho»**: Felipe marca hecha una tarjeta cuando aplicó la mayor parte, y descartada cuando
    la mayor parte no tenía sentido. Al verificar una «hecha», comprobá qué ítems se aplicaron y cuáles no, y anotalo
    (los que no, si siguen teniendo sentido, pueden volver como tarjeta nueva más chica).

Herramienta para armar el «dónde» y los datos de cada campaña: `python scripts/ficha_campana.py "<nombre de campaña>"`
(grupos, keywords con nivel de calidad y gasto, negativas, anuncios vigentes con id, fuerza y rendimiento de cada
recurso, y términos de búsqueda).

Calidad de cada tarjeta:

- Español rioplatense, concreto, con números y el período («oct 2026: 23 clics, ARS 41.000»).
- Título corto que diga la acción; el detalle explica qué hacer en Google Ads, por qué (datos) y qué se espera.
- Prioridad: **alta** = plata mal gastada o campaña frenada; **media** = mejora de relevancia/CTR; **baja** = orden.
- Como mucho ~10 nuevas por mes: mejor pocas y sólidas.
- Reglas de marca (no negociables): Control Union y PCU **certifican, auditan, inspeccionan, verifican**; nunca
  «asesoramos» ni «diseñamos tu estrategia». Peterson Solutions **acompaña, co-desarrolla, prepara para
  certificar**; nunca «certificamos». No se mezclan marcas. Los títulos de anuncio propuestos ≤ 30 caracteres y las
  descripciones ≤ 90 (ver skill `paid-media-pcu`).

## 6. Escribir y aplicar la revisión

1. Escribí `informe/revision_sem_<R>.json` con el formato del encabezado de `scripts/aplicar_revision.py`:
   - `nuevas`: clave `<MARCA>:SEM:campana:<campaña>@<R>` (minúsculas, guiones), `campana` con el nombre **exacto**
     de la campaña actual, `grupo` si aplica, y `evidencia` con **`ficha: "campana"`** y `acciones` (`anuncio`,
     `keywords`, `negativas`, `estructura`, `pausa`, `landing`, `revisar`). Campos de la ficha «campana» (ver el
     ejemplo real de ISCC y EUDR en `informe/unificacion_sem_2026-10.json`):
     - `campana` (o `campanas` si son varias), `unidad`, `resumen`, `por_que`, `ya_hecho`, `datos_hasta`.
     - `pasos`: `[{accion, titulo, donde, detalle, items: [{accion, tipo, texto, concordancia, destino, reemplaza,
       prioritario, opcional, motivo}]}]` en el orden en que hay que hacerlos (regla 6).
     - `keywords`: `[{texto, concordancia: exacta|frase|amplia, grupo, accion, motivo}]`.
     - `negativas`: `[{texto, concordancia, nivel: campaña|grupo, grupo, motivo}]` y `negativas_decision`.
     - `anuncios`: `[{grupo, anuncio_id, anuncio_desc, accion, motivo, url, gasto_ars, clics, ventanas, titulos_hoy,
       descripciones_hoy, quitar: [{texto, motivo}], titulos_propuestos: [{texto, motivo, prioritario, reemplaza}],
       descripciones_propuestas: [...], terminos: [{termino, relacion, coste, clics}], nota}]`.
     - `organico` (`query`, `impr`, `pos`), `organico_desde`, `organico_hasta`.
   - `ajustes`, `descartes` (siempre con `motivo`) y `verificadas`.
2. `python scripts/aplicar_revision.py informe/revision_sem_<R>.json` — valida (marcas, vocabulario, campañas,
   prioridades) y genera el `.sql`. Si marca errores, corregí el JSON.
3. Ejecutá el `.sql` con `execute_sql` y verificá:
   `select estado, count(*) from seo_sem.recomendaciones where origen = 'revision-mensual-<R>' or actualizada_por = 'Revisión mensual (Claude)' group by 1;`

El SQL ajusta tarjetas en «propuesta» y «en proceso», descarta solo «propuestas» y verifica «hechas»; nunca borra
filas, nunca mueve una tarjeta del equipo de columna ni toca hechas o descartadas (salvo verificarlas). Cada ajuste
queda con fecha en `evidencia.revisiones` y el tablero marca la tarjeta como «Actualizada».

## 6 bis. Revisión SEO (mismo mes, mismas reglas)

Con Search Console de M (y GA4 de las landings), revisá también las tarjetas de «SEO · sitios» (`tipo = 'SEO'`,
ficha `seo`): las mismas decisiones del paso 5 (ajustar / descartar / verificar / nuevas, ≈5 nuevas como máximo) y
las reglas 6 a 10. Formato de la ficha `seo` (sitio, páginas, pasos con `items` de title, meta, H1, texto, 301):
`informe/concretar_2026-10/BRIEF.md`, sección SEO; se valida con `validar_seo` de `aplicar_revision.py`. Lo que se
compara: impresiones, clics, CTR y posición de las páginas y queries de cada tarjeta, M contra M-1, por **tema** (nunca
por string exacto) y separando el país cuando el sitio junta varios (northamerica: CUC USA y Canadá). Las tarjetas
SEO van en el mismo `revision_<R>.json` (clave `<MARCA>:SEO:<sitio>:<tema>`).

## 6 ter. Impacto de las hechas

La vista «Impacto» del tablero cruza cada tarjeta SEM «hecha» con `seo_sem.cambios_ads` y compara 28 días antes del
primer cambio con los días posteriores al último (`src/utils/impacto.ts`). En el resumen, nombrá las hechas con
resultado negativo y las que tienen menos de la mitad de los ítems aplicados: son candidatas a una tarjeta de ajuste.

## 7. Resumen

Escribí `informe/revision_sem_<R>.md`: datos usados (hasta qué día, por fuente), qué se cargó al tablero, cuántas
tarjetas SEM y SEO nuevas / ajustadas / descartadas / verificadas y por qué, **las «en proceso» que se actualizaron
(qué cambió)**, las «en proceso» que parecen obsoletas, y cualquier problema de datos o de acceso.
El mensaje final de la sesión es un resumen corto de eso: el detalle vive en el tablero.

## Límites

- Google Ads, Search Console y GA4 son **solo lectura**: nunca se cambia nada en las cuentas.
- No se modifica el código del tablero. En la compu no se hace commit en esta rutina. En la nube sí, porque la VM se
  borra al terminar: se commitea solo lo generado dentro de `analisis/` (datos, informe, `docs/memoria/`) y se abre un
  PR a `main`, como dice `nube/TAREAS.md`.
- Nunca se pegan tokens, `client_secret.json`, `token*.json` ni `google-ads.yaml` en ningún lado.
