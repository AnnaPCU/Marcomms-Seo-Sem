# Decisiones

Registro corto de por qué las cosas son como son. Se agrega arriba.

## 2026-10-02 — Vista «Día a día», rotación desplegable y PCU como cliente

- **Día a día** (tercera vista de Presupuesto, junto a Mes y Promedio por día): calendario del mes con el gasto de cada
  día sobre el presupuesto diario de las campañas activas, detalle del día elegido (por defecto, el último con datos)
  y una grilla campaña × día. Rojo: más de un 5% por encima; rojo claro: activa sin gasto; verde: dentro; gris: sin
  presupuesto. Los datos vienen de `seo_sem.metricas_dia` (migración 0004), que carga `publicar.py` desde
  `informe/datos_gasto_diario.json` (`ads_diario.py` del proyecto de análisis). Se cruza por `ads_id`.
  Límite: el presupuesto de referencia es el que la campaña tiene hoy; Google puede gastar hasta el doble en un día.
- **Rotación de inversión**: «Ver N más» despliega el resto de cada lista y «Ocultar» la vuelve a cerrar.
- **Consumo por cliente** con divisores; PCU se muestra como «Peterson Control Union (ISO)».
- Los scripts reconocen también el naming estándar del equipo (`CU_US_SEARCH_…`) para marca y país.

## 2026-09-30 — Tipo de mejora, orgánico en el plan y tarjetas relacionadas

- **Tipo de mejora** (`evidencia.acciones`): anuncio, palabras clave, negativas, grupos y campañas, pausar o
  presupuesto, landing, revisar o decidir. Lo calcula `exportar_recomendaciones.py` con reglas sobre el texto de la
  mejora (no del problema); una tarjeta puede tener varios. En SEM hay una fila de chips para filtrar (`?accion=`)
  y cada tarjeta muestra sus tipos.
- **Orgánico en las tarjetas del plan**: mismo método que las de anuncio (los temas de las keywords de la campaña →
  búsquedas de Search Console desde el país de la campaña), con piso de 10 impresiones para no mostrar coincidencias
  sueltas. Si no hay búsquedas, se dice que es un hueco de contenido. Las del plan sin campaña no muestran el bloque.
- **Tarjetas relacionadas**: el detalle lista las otras tarjetas de la misma campaña, así desde una mejora del
  plan se llega a su propuesta de anuncio y al revés.

## 2026-09-30 — Arrastre, fichas completas y claves estables

- **Arrastre**: la animación de entrada dejaba un `transform` en el contenedor de la página y todo lo que usa
  `position: fixed` (la tarjeta que se arrastra, los diálogos) quedaba ubicado respecto de la página. La
  animación ya no deja transform, y la copia arrastrada y los diálogos se montan en `<body>` con un portal.
- **Fichas completas** en el detalle de cada tarjeta, con la misma información que los informes PDF: qué dice hoy
  el anuncio, qué buscó la gente (con relación fuerte/parcial/nula explicada), cómo lo buscan en orgánico (con
  impresiones y posición explicadas), diagnóstico, qué quitar y títulos/descripciones propuestos con su largo.
  Los datos viajan en `evidencia` (campo `ficha`: `anuncio` o `plan`).
- **Claves estables** (migración 0003): la clave de las tarjetas SEM ya no incluye el nombre de la campaña en
  Google Ads, porque cambia seguido. Formato: `MARCA:SEM:plan:<unidad>:<pain point>` y
  `MARCA:SEM:anuncio:<campaña del informe>:<grupo>`. Se migraron las 52 conservando estado e historial.

## 2026-09-30 — Rediseño con el lenguaje de MarComms Reports

- **Barra superior blanca fija con pestañas**, en lugar de barra lateral: igual que Reports, así el equipo
  navega las dos herramientas de la misma forma.
- **Títulos de sección azules en mayúsculas con línea**, indicadores con borde de color (azul, verde, dorado,
  rojo) y uno destacado en azul noche, franjas azul noche para los bloques de acción y embudo
  impresión → clic → conversión con degradé azul noche → azul → verde.
- **Paleta ampliada**: índigo, verde, dorado y rojo como acentos. Ninguno es un color de marca de los clientes.
- **Loader**: el símbolo MC en órbita con degradé y mensajes que rotan; esqueletos con brillo dentro de cada vista.
- **Favicon cuadrado** recortado al símbolo MC (el anterior era 128×75 y se estiraba).
- **El informe de gasto no se manda más por chat**: todo se consulta en la web.

## 2026-09-30 — Presupuesto en el Inicio

- **El Inicio es el seguimiento de presupuesto.** Réplica en vivo del informe de gasto: cliente → país → campaña →
  grupo, por mes o por día. Pedido de Felipe: poder rotar inversión entre campañas.
- **Semáforo por ritmo de gasto**: rojo si la campaña gasta por día más de un 5% sobre su presupuesto diario o no
  gasta nada; verde en el medio; gris si no tiene presupuesto activo. Se mide contra el presupuesto por día porque el
  consumo acumulado del mes todavía no terminó y engaña.
- **Consumo 0–100 con marca de «dónde debería estar hoy»**, proyección al cierre y listas de topeadas (≥95% del
  ritmo) y ociosas (<50%), tomado como referencia de Dashbo (control de presupuestos para agencias).
- **Solo cuenta el presupuesto de campañas activas.** Una pausada o eliminada no lo puede gastar.
- **Gasto por grupo en `metricas_grupo_mes`** (migración 0002) y días cubiertos en `metricas_mes`.
- **Prioridad en rojo, ámbar y verde.** Ámbar de Tailwind, no el amarillo de Peterson (#f1e747).
- **Filtro por país en SEM**: cliente → país → campaña → grupo. Las tarjetas sin campaña usan el país de su unidad.
- **País por palabra clave en el nombre de la campaña**, no por prefijo: los nombres de ISO 27001 cambiaron tres
  veces en una semana («PCU Argentina» → «PCU Tech» → «PCU - Argentina»). El catálogo se actualiza por id de Ads.

## 2026-09-28 / 29 — Arranque

- **Identidad MarComms, no la de los clientes.** El tablero es de la agencia interna. Control Union y
  Peterson aparecen como chips de texto en la paleta MarComms; nunca con sus colores ni logos, porque el
  manual del grupo no admite piezas que mezclen las dos marcas.
- **Esquema `seo_sem` dentro del proyecto MarComms Hub, no proyecto propio.** Se quería un proyecto nuevo,
  pero el plan gratuito de Supabase permite 2 proyectos activos por usuario sumando todas sus organizaciones
  y la cuenta ya los tenía (uno en marcomms-hub y otro en otra organización). Un esquema aparte da el mismo
  aislamiento de datos y RLS, comparte el login y no cuesta nada. Regla: nunca tocar `public` ni `auth.users`.
- **Restricción de dominio en las políticas RLS**, no con un trigger sobre `auth.users`, para no afectar al
  Hub. Una cuenta ajena puede iniciar sesión pero no lee ni escribe nada de `seo_sem`.
- **Contraseña compartida en vez de login por correo.** Felipe no quiere que cada persona entre con su mail:
  una sola cuenta interna de Auth y una contraseña de equipo, sin nombre ni usuario, como en MarComms Reports.
  El historial registra «Equipo MarComms»; si más adelante hace falta saber quién movió qué, se agrega el nombre. Costo: si alguien filtra la
  contraseña, se cambia desde el dashboard de Supabase y listo.
- **Carga de datos por SQL generado** (`publicar.py --sql`) en lugar de la API con service role key: no
  requiere secretos en ninguna máquina y el archivo queda versionado en `supabase/seed/`.
- **Clave estable por recomendación** (`marca:tipo:campaña|sitio:slug`). Es lo que permite renovar cada mes
  sin duplicar tarjetas ni pisar el estado que alguien ya movió.
- **Las recomendaciones no se escriben en la web.** Salen de los informes del proyecto de análisis y se
  cargan por script. La web es para decidir y seguir, no para redactar.
- **Métricas por mes calendario**, del 1 al último día con datos. Felipe pidió que la vista mensual sea el mes
  real y no una ventana móvil; el gasto por día sale de dividir por los días con datos.
- **RLS abierto para autenticados.** Equipo de pocas personas, todas del grupo; no hay roles por ahora.
- **Una rama, sin staging.** `npm run verificar` antes de cada push reemplaza al entorno de prueba.
