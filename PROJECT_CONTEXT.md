# Marcomms SEO-SEM — contexto del proyecto

## Qué es

Un tablero web donde el equipo de MarComms sigue, mes a mes, las mejoras propuestas para las campañas de
Google Ads (SEM) y para los sitios (SEO) de sus dos clientes internos: Control Union y Peterson Solutions.
Cada recomendación es una tarjeta que se arrastra entre cuatro columnas: propuesta, en proceso, hecha,
descartada. Cada movimiento queda registrado con quién y cuándo; descartar exige un motivo.

## De dónde salen las tarjetas

Del proyecto de análisis `Optimizaciónes SEO-SEM/proyecto` (Python), que cruza Google Ads por API con el
histórico de Search Console. Sus informes se traducen a recomendaciones con una **clave estable**
(`marca:tipo:campaña|sitio:slug`) para que el mismo hallazgo no se duplique cuando se vuelve a correr el
análisis el mes siguiente. Origen de cada tipo:

| Origen | Tipo | Segmentación |
|---|---|---|
| Plan de mejoras unificado | SEM | cliente → unidad → campaña |
| Propuestas de anuncios | SEM | cliente → campaña → grupo de anuncios |
| Recomendaciones SEO | SEO | cliente → propiedad de Search Console |

## Modelo de datos (Supabase, esquema `seo_sem` del proyecto MarComms Hub)

- `campanas`, `grupos`: catálogo real de la cuenta de Ads, sincronizado desde el snapshot de estructura.
- `recomendaciones`: las tarjetas. `estado`, `orden`, `actualizada_por`, `mes_cierre`, `motivo_descarte`
  son del tablero; `titulo`, `detalle`, `evidencia`, `prioridad` los renueva el loader.
  `verificada_api` se reserva para marcar automáticamente lo que la API confirme aplicado (pendiente).
- `recomendacion_eventos`: historial de cambios de estado.
- `extracciones`: última corrida de cada fuente y hasta qué fecha llegan los datos.
- `metricas_mes`: gasto, clics y conversiones por campaña y mes calendario (del 1 al último día con datos
  al momento de la extracción; se reemplaza al volver a correr el loader).
- `metricas_grupo_mes`, `metricas_dia`: lo mismo por grupo de anuncios y por campaña y día (vista «Día a día»).
- Histórico de Ads (desde feb 2026): `ads_historico.py` junta la cuenta actual («Control Union - (en ARG)», en pesos,
  desde jul 2026) y la anterior («Peterson Technologies», en euros, feb–jul 2026; Growr y campañas sin prefijo de marca
  no entran). Los euros se pasan a pesos con el promedio mensual del tipo de cambio oficial del BCRA; `metricas_mes`
  guarda `moneda_original`, `coste_original` y `tipo_cambio`. `campanas.cuenta` = 'actual' | 'anterior' (las dos cuentas
  repiten nombres: el nombre es único por cuenta). Se carga con `publicar.py --solo historico` (cruza por `ads_id`).
  En el tablero: el período por defecto es el último mes cerrado y se pueden elegir los anteriores; la vista
  «Histórico» muestra la evolución mes a mes (Presupuesto y Sitios). GA4 tiene datos desde dic 2025.
- `ga4_sitio_mes`: Google Analytics 4 por sitio y mes (pestaña «Sitios · GA4»): sesiones, visitas con interacción,
  canales, contactos reales y páginas de entrada pagas y orgánicas. Sale de `proyecto/scripts/ga4_export.py`
  (`informe/datos_ga4.json`) y se carga con `scripts/publicar.py --solo ga4`. Contactos reales = formularios
  Gravity Forms (`form_id` «gform_…») + clics a email fuera de páginas de empleo, academia y reclamos; los
  formularios de HubSpot embebidos no llegan a GA4.

## Acceso

Contraseña compartida del equipo. La app inicia sesión en Supabase Auth con la cuenta interna del tablero
(`seo-sem@onepeterson.com`, cuenta de Auth sin buzón) y la contraseña que escribe la persona; no hay usuarios
individuales, así que el historial registra «Equipo MarComms». Las políticas RLS de `seo_sem` exigen sesión con correo
`@onepeterson.com` o `@controlunion.com`, que esa cuenta cumple. No se toca `auth.users` para no interferir con el Hub.

## Qué no hace todavía

- No lee Google Ads ni Search Console en vivo: todo entra por `scripts/publicar.py` (modo `--sql`).
- No marca sola `verificada_api`; el análisis mensual ya detecta negativos y exactas aplicadas, falta
  conectarlo con la clave de cada tarjeta.
- No tiene presupuestos futuros. La tabla `metricas_mes` es el lugar donde van cuando existan.
