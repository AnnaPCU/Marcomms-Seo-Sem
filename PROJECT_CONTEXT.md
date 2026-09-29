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

## Acceso

Supabase Auth del proyecto compartido. Google o enlace por correo; las políticas RLS de `seo_sem` solo dejan
pasar sesiones con correo `@onepeterson.com` o `@controlunion.com` (otra cuenta puede iniciar sesión pero no ve
nada). No se toca `auth.users` para no interferir con el Hub.

## Qué no hace todavía

- No lee Google Ads ni Search Console en vivo: todo entra por `scripts/publicar.py` (modo `--sql`).
- No marca sola `verificada_api`; el análisis mensual ya detecta negativos y exactas aplicadas, falta
  conectarlo con la clave de cada tarjeta.
- No tiene presupuestos futuros. La tabla `metricas_mes` es el lugar donde van cuando existan.
