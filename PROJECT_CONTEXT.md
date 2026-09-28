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

## Modelo de datos (Supabase)

- `campanas`, `grupos`: catálogo real de la cuenta de Ads, sincronizado desde el snapshot de estructura.
- `recomendaciones`: las tarjetas. `estado`, `orden`, `actualizada_por`, `mes_cierre`, `motivo_descarte`
  son del tablero; `titulo`, `detalle`, `evidencia`, `prioridad` los renueva el loader.
  `verificada_api` se reserva para marcar automáticamente lo que la API confirme aplicado (pendiente).
- `recomendacion_eventos`: historial de cambios de estado.
- `extracciones`: última corrida de cada fuente y hasta qué fecha llegan los datos.
- `metricas_mes`: gasto, clics y conversiones por campaña. Hoy se carga la ventana móvil de 31 días que
  termina en el mes indicado (la API se consulta por ventana, no por mes calendario).

## Acceso

Supabase Auth. Google o enlace por correo; un trigger sobre `auth.users` rechaza cualquier cuenta que no sea
`@onepeterson.com` o `@controlunion.com`. RLS: solo usuarios autenticados, acceso completo (equipo chico).

## Qué no hace todavía

- No lee Google Ads ni Search Console en vivo: todo entra por `scripts/publicar.py`.
- No marca sola `verificada_api`; el análisis mensual ya detecta negativos y exactas aplicadas, falta
  conectarlo con la clave de cada tarjeta.
- No tiene presupuestos futuros. La tabla `metricas_mes` es el lugar donde van cuando existan.
