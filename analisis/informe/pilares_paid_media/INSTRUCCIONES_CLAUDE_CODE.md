# Carga del histórico de Google Ads en Pilares → Paid Media

Para el Claude Code que trabaja en el repo **MarComms Hub** (`Documentos/MarComms Hub`, Supabase `cogdfbonpvvuzhurmvlq`).

## Qué hay que hacer

Cargar en la tabla `public.campaigns` (tipo `paid`, la que se ve en Pilares → Paid Media) **una fila por campaña de
Google Ads** del histórico completo de las dos cuentas del grupo, a partir de los archivos de esta carpeta.

## Archivos

Un archivo por marca: **los datos de Control Union y de Peterson Solutions nunca van en el mismo archivo**.

| Archivo | Qué es | ¿Se carga? |
|---|---|---|
| `paid_media_google_ads_cu.json` / `.xlsx` | 31 campañas de Control Union | Sí |
| `paid_media_google_ads_ps.json` / `.xlsx` | 8 campañas de Peterson Solutions | Sí |
| `paid_media_google_ads_pcu.json` / `.xlsx` | 4 campañas «PCU» de ISO 27001 (Argentina y España), las paga Control Union España | Sí |

Usá el **JSON** para la carga; el Excel es el mismo contenido para que lo revise una persona.
Cada campaña del JSON trae un objeto `hub` con la fila lista para la tabla. El resto de las claves son el detalle de origen.
El arreglo `mensual` tiene gasto, impresiones, clics y conversiones por mes (por si la app quiere mostrar la evolución).

Las 23 campañas sin prefijo de marca de las cuentas (Growr y Peterson Technologies, 2024–2026) **no se cargan**, por
decisión de Felipe (22 oct 2026). No vienen en estos archivos: no las busques ni las agregues.

## Mapeo (ya resuelto en `hub`)

| `hub` | Columna / campo de la app | Valor |
|---|---|---|
| `type` | `type` | `"paid"` |
| `name` | `name` | Nombre exacto de la campaña en Google Ads |
| `country` | `country` | Argentina, Canada, España, Portugal, Estados Unidos (mismos textos que ya usa la app) |
| `business_unit` | `business_unit` | `Control Union` / `Peterson Solutions` / `PCU` |
| `data.facturar_a` | Quién paga (nuevo) | `{unidad, pais}`. En CU y PS es la misma unidad y país de la campaña; en las 4 PCU es `Control Union` / `España` |
| `platform_investment` | `platform_investment` → «Inversión oficina (USD)» | Gasto real total en USD |
| `completed_steps` | `completed_steps` | `brief`, `creativities`, `launch` (los ids de `CAMPAIGN_STEPS.paid`) |
| `completed_at` | `completed_at` | Último día con impresiones si la campaña ya no está activa; `null` si sigue activa |
| `data.platforms` | Plataformas | `["google"]` |
| `data.paidMode` | Modalidad | `always_on` / `one_shot` (inferido: one_shot si tiene fecha de fin o es de evento) |
| `data.duration` | Duración | Texto: `"N días · desde a hasta"` o `"Sin fecha de fin · desde …"` |
| `data.objective` | Objetivo | `posicionamiento` / `conversion` (inferido de la estrategia de puja; hoy casi todas son Maximizar clics → posicionamiento) |
| `data.detail` | Detalle / Brief | Resumen: tipo, puja, presupuesto diario, ubicaciones, idiomas, grupos, keywords, landing, ids |
| `data.google_ads` | (nuevo, no lo pisa la UI) | Clave externa, ids, estado, landings, resultados (impresiones, clics, CTR, CPC, conversiones, CPL) y gasto en moneda original |

`saveCampaign`/`toRow` arma `data` con `{...obj.data}` y después pisa solo `platforms, paidMode, duration, objective,
detail`: confirmá en `src/services/campaignsService.js` que `data.google_ads` sobrevive a una edición desde la UI. Si no
sobrevive, ajustá el servicio para que conserve las claves extra de `data`.

## Reglas de la carga

1. **Sin duplicados.** La clave es `data.google_ads.clave_externa` (`gads:<cuenta>:<id>`, o dos ids unidos con `+` cuando la
   campaña se migró de la cuenta vieja a la nueva en jul 2026). Si ya existe una fila con esa clave, se actualiza; si no, se inserta.
   Así la carga se puede repetir más adelante con datos nuevos.
2. **No pisar lo que carga el equipo a mano**: `budget` (Fee MarComms), `billing`, `service_owner`, `hubspot_link`,
   `deals_created`, `quotation_validated`, `comments`, `program_id`, `plan_id`. En inserts nuevos dejalos con el valor por defecto.
3. **No tocar** las dos filas de prueba que ya están en la tabla («test programa · Paid Media» y «smeta»).
4. **PCU** (decisión de Felipe, 22 oct 2026): se cargan con `business_unit = "PCU"` y quien paga es **Control Union España**
   (`data.facturar_a`), también las dos que corren en Argentina. Dos ajustes en la app:
   - «PCU» no está en las unidades de `src/constants/markets.js` (`unitsForCountry`): agregala para Argentina y España, o el
     select de Unidad no la va a mostrar.
   - La app no tiene hoy un campo de «quién paga». Si el módulo de Facturación agrupa por país + unidad de la campaña,
     estas 4 tienen que sumar a **España · Control Union**: usá `data.facturar_a` (o el campo que ya use la versión en
     producción, p. ej. `billing`/`plan_id`, si existe) y mostralo en la ficha de Paid Media.
5. Opcional, a confirmar con Felipe: `created_at = data.google_ads.primer_dia` para que el listado quede en orden histórico.
6. Verificá después de cargar: cantidad de filas `type = 'paid'` con `data->'google_ads'` por `business_unit`, y la suma de
   `platform_investment` contra la sección «Totales» de abajo.

## Cómo se calcularon los números

- Fuente: Google Ads API (solo lectura), todas las campañas de cualquier tipo y estado (activas, pausadas y eliminadas) de
  «Control Union - (en ARG)» (1606422184, ARS, desde jul 2026) y «Peterson Technologies» (6527967282, EUR, desde dic 2024),
  hasta el 21 oct 2026.
- USD: cada mes se convirtió con el promedio mensual del tipo de cambio de referencia del BCRA (pesos por USD y por EUR).
  La hoja «Tipo de cambio» del Excel tiene los valores usados.
- Las campañas que nunca tuvieron impresiones están en la hoja «No publicadas» del Excel y no se cargan.
- Alcance no existe en campañas de Search: no viene.
- Fee MarComms, responsable, ticket de HubSpot y deals no existen en Google Ads: se completan a mano en la herramienta.

## Totales (para verificar)

| Archivo | Campañas | Inversión USD |
|---|---|---|
| CU | 31 | 5.707,81 |
| PS | 8 | 1.049,45 |
| PCU (paga CU España) | 4 | 878,16 |

Se regenera con `Optimizaciónes SEO-SEM/proyecto/scripts/ads_pilares_paid_media.py`.
