---
name: informes-landing-con-marca
description: "Los informes de consultas de landing van siempre como página HTML lindo, amigable y dinámico, con el manual de marca de CU o PS según la landing (generador informe_landing.py)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 459b6f72-44b4-47d0-9fdd-b6193cfc0f40
  modified: 2026-11-19T12:59:15.219Z
---

Felipe (17 nov 2026): el informe de cada consulta de landing tiene que ser **siempre** sólido, estético, amigable y
dinámico, y respetar el manual de marca de **Control Union o Peterson Solutions según la landing** (una sola marca por pieza).

**Why:** el .md suelto no le sirve como entregable; quiere algo que se lea y se use fácil.
**How to apply:** escribir el contenido en `proyecto/informe/landings/<sitio>_<pagina>_<AAAA-MM-DD>.json` (`"marca": "cu"|"ps"`)
y correr `python scripts/informe_landing.py <json>` → `.html` autocontenido al lado (logo y Sansa embebidos desde
`proyecto/marca/<cu|ps>/`, Ubuntu de Google Fonts). Trae KPIs, gráficos, pasos plegables con «Copiar» y contador de
caracteres, check de «hecho» y qué medir. Texto para Felipe en español neutro
formal (sin voseo, va con marca); lo que se carga en el sitio, en el idioma del sitio. CU: barra cyan arriba, barra
azul abajo desde la derecha, tagline «THE PROOF TO YOUR PROMISE» al pie, nunca «asesoramos/estrategia». PS: tema
aqua/navy/wheat, tagline «For the world, for ourselves, for our families», nunca «certificamos» — antes del primer
informe PS leer `references/peterson.md` del skill manual-de-marca-pcu y ajustar el tema. Verificar en el navegador
integrado (escritorio y 375 px). Publicarlo como Artifact solo si Felipe lo pide (lleva el logo real).

**Contenido (Felipe, 17 nov 2026, para siempre):**
- **Nada de recomendaciones de ajuste de campañas pagas** (puja, CPC, keywords, anuncios, ubicaciones). Los datos de
  SEM sí se usan como evidencia en el «por qué» de las recomendaciones de página/sitio (p. ej. términos de búsqueda reales).
- Sin avisos ni aclaraciones sobre el estado de campañas pagas (nada de «la campaña está en pausa…»).
- Cabecera solo con el logo: sin etiqueta de documento ni fecha, sin línea «unidad · sitio», sin línea de períodos.
- Sin tarjetas de Problema / Solución arriba; sin tabla «Los números»; sin «Límites de los datos» (los límites se
  mencionan, si hace falta, en la respuesta del chat).
- Pie solo con la tagline: nada de «Revisión interna · fuentes · datos al…».
- Título = solo el nombre de la landing en español (campo `nombre`, p. ej. «Certificación PrimusGFS»), nunca un titular
  con el diagnóstico; debajo la URL.
- Queda: nombre, URL, KPIs, diagnóstico con gráficos, paso a paso con texto exacto y «qué medir». El generador ya lo aplica.

**Generador (19 nov 2026):** segundo gráfico = `competencia` (mancuerna de posiciones) o `ranking` (barras horizontales,
`filas: [{etiqueta, valor, nota?, destacar?}]`). Tipos de paso usados: SEO, AEO, Técnico (los filtros aparecen solos).
El navegador integrado ya no abre `file://`: para revisar, `preview_start` «informes-landings» (http.server 8765 en
`.claude/launch.json`). Primeros informes PS: americas «preparacion-para-certificaciones» y «bioenergia» (19 nov).
Cuando piden «SEO y AEO», AEO = párrafo de entrada que responde primero, lista de pasos, FAQ de 30–40 palabras por
respuesta y JSON-LD Service + FAQPage (aclarar que el rich result de FAQ ya no se muestra salvo gobierno/salud).
Ver [[felipe-perfil]], [[mapa-del-proyecto]], [[nombre-cuc-usa]].
