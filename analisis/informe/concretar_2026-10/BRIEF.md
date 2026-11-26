# Concretar las tarjetas del tablero (28 oct 2026)

Pedido de Felipe Señorans (Marketing Campaign Specialist, Peterson Control Union) sobre el tablero Marcomms SEO-SEM:

> «No entiendo en el punto 1 qué negativa poner, qué exactas poner en el punto 2. Necesito que cada vez que hacés una
> propuesta comentes concretamente qué hacer. Revisá este caso, corregilo y mejorá el resto de propuestas a nivel
> SEO-SEM cuando consideres que puede suceder algo por el estilo.»

Tu trabajo: reescribir un lote de tarjetas viejas para que **cada paso diga exactamente qué cargar o cambiar, dónde y por
qué**, con datos reales. Escribís **un solo archivo JSON** (la ruta te la da tu encargo). No toques ningún otro archivo,
no escribas en la base de datos, no cambies nada en Google Ads, Search Console, GA4 ni en los sitios: todo es solo lectura.

Leé antes `proyecto/CLAUDE.md` (marcas, reglas de los cruces, límites de los datos) y `proyecto/RUTINA_REVISION_MENSUAL_SEM.md` §5.

## Fuentes

- Tarjetas viejas: `proyecto/informe/recomendaciones.json` (buscá por `clave`). El texto de septiembre es punto de
  partida, **no verdad**: verificá todo contra los datos actuales y decí si algo ya se hizo.
- Ejemplos del formato bueno (copiá el estilo y el nivel de detalle): `proyecto/informe/unificacion_sem_2026-10.json`,
  en particular `CU:SEM:anuncio:cu-argentina-biocombustible:iscc` y `CU:SEM:anuncio:cu-espana-ifs:food-safety`.
- SEM, por campaña: `python proyecto/scripts/ficha_campana.py "<nombre exacto de campaña>" --terminos 60` → grupos,
  keywords (concordancia, nivel de calidad, clics y gasto), negativas de campaña y de grupo, anuncios activos con id,
  fuerza y textos, y términos de búsqueda con gasto. Estructura al 21 oct 2026; métricas 1 sep – 20 oct 2026.
  CSV crudos en `proyecto/datos/ads/api/` (estructura_20261021/, y por cuenta `ads_*_{terminos,keywords,anuncios,recursos}_2026-09-01_2026-10-20.csv`).
- Orgánico: `proyecto/datos/gsc-historico/{cu,ps}/gsc_*_hist_query_page.csv` (columnas brand, window, property, site,
  query, page, clicks, impressions, ctr, position) y `gsc_*_hist_pages.csv`, `gsc_*_hist_queries.csv`. Datos hasta 14 sep 2026.
  Análisis SEO de septiembre: `proyecto/informe/datos_seo.json` y «Recomendaciones SEO para los sitios - sep 2026.pdf».
- Sitios públicos: podés leer la página en vivo (WebFetch) para copiar el title, la meta description y el H1 actuales.
- GA4 por página: `proyecto/informe/datos_ga4_paginas.json` si existe.

Montos en pesos argentinos (ARS) con punto de miles («ARS 12.345»). Fechas: «1 sep – 20 oct 2026».

## Reglas (no negociables)

1. **Una acción, una tarjeta; una tarjeta por campaña.** Si dos tarjetas viejas tocan la misma campaña, salen en una.
   Si una tarjeta vieja abarca dos campañas con acciones distintas, se parte en una por campaña. Una sola acción que
   abarca varias campañas (p. ej. «pausar las dos») va en una tarjeta con `evidencia.campanas`.
2. **Cada paso con `items`**: la lista exacta. Nada de «las negativas de la tabla», «de abajo», «Anexo A»,
   «negativos de marcas del agro», «pausar el resto», «mirar términos», «revisar el anuncio»: se escribe cada negativa,
   cada keyword, cada texto. Si un paso es una decisión, el item es la pregunta concreta y qué hacer según la respuesta.
   Si hay un número (tope de CPC, presupuesto), se da el número y de dónde sale.
3. **Siempre dónde**: nombre completo de la campaña como está en Google Ads, grupo e id del anuncio.
4. **Motivo con datos** en cada keyword, negativa, título y descripción. Prioritarias (`prioritario: true`) solo las que
   de verdad conviene hacer; el resto `opcional: true`.
5. **No inventar**: cada cifra sale de los archivos. Lo que no se puede verificar (alcance de un servicio, versión de una
   norma, acreditación) va marcado «confirmar con la unidad» y nunca como prioritario.
6. **Marcas**: Control Union y PCU certifican, auditan, inspeccionan, verifican; nunca «asesoramos», «consultoría»,
   «te explicamos», «te preparamos», «apoyo/soporte». Peterson Solutions acompaña, co-desarrolla, prepara para
   certificar; nunca «certificamos». Idioma del anuncio: el del mercado (España: tú; Argentina: vos; Portugal: portugués
   europeo; EE. UU./Canadá: inglés). Títulos ≤ 30 caracteres, descripciones ≤ 90. Textos de la tarjeta: español rioplatense.
7. **Google Ads**: no se puede cambiar la concordancia de una keyword existente → item «agregar» la nueva + item «pausar»
   la vieja. Un anuncio tiene máximo 15 títulos y 4 descripciones: si está lleno, cada propuesta reemplaza a uno
   (`reemplaza` con el texto exacto actual, copiado del snapshot). Negativas: no cubren plurales ni variantes con tilde.
8. Si una tarjeta vieja ya no tiene sentido (se hizo, la campaña se eliminó, los datos la contradicen), no la reescribas:
   ponela en `descartes` con el motivo y el dato.

## Formato SEM (ficha «campana»)

```json
{"tarjetas": [{
  "clave": "clave existente que se reescribe (o nueva: <MARCA>:SEM:campana:<slug-campaña>@2026-10)",
  "marca": "CU|PCU|PS", "campana": "nombre exacto o null", "grupo": "grupo principal o null",
  "titulo": "≤ 140 caracteres: la acción concreta + el dato que la justifica",
  "detalle": "2–4 frases: qué hacer y por qué",
  "prioridad": "alta|media|baja",
  "unifica": ["otras claves viejas que quedan dentro de esta (se descartan)"],
  "evidencia": {
    "ficha": "campana", "unidad": "España|Portugal|Argentina|Canadá|Estados Unidos",
    "campana": "…" , "campanas": ["solo si son varias"],
    "acciones": ["anuncio","keywords","negativas","estructura","pausa","landing","revisar"],
    "resumen": "una frase", "por_que": "datos del período", "ya_hecho": "qué de lo de septiembre ya está (o «Nada…»)",
    "pasos": [{"accion": "negativas", "titulo": "Sumar 6 negativas de campaña", "donde": "<campaña> › toda la campaña",
               "detalle": "…", "items": [
        {"accion": "agregar", "tipo": "negativa", "texto": "bonos", "concordancia": "amplia", "destino": "Toda la campaña", "motivo": "«bonos de carbono»: ARS 4.321 por 2 clics."}]}],
    "keywords": [{"texto","concordancia","grupo","accion","motivo"}],
    "negativas": [{"texto","concordancia","nivel":"campaña|grupo","grupo","motivo"}], "negativas_decision": "…",
    "anuncios": [{"grupo","anuncio_id","anuncio_desc","accion","motivo","url","gasto_ars","clics","ventanas",
                  "titulos_hoy","descripciones_hoy","quitar":[{"texto","motivo"}],
                  "titulos_propuestos":[{"texto","motivo","prioritario","reemplaza"}],"descripciones_propuestas":[…],
                  "terminos":[{"termino","relacion":"fuerte|parcial|nula","coste","clics"}],"nota"}],
    "organico": [{"query","impr","pos"}], "organico_desde": "España", "organico_hasta": "14 sep 2026",
    "datos_hasta": "21 oct 2026"}}],
 "descartes": [{"clave": "…", "motivo": "…"}]}
```

Items: `accion` ∈ agregar | pausar | quitar | reemplazar | cambiar | crear | decidir; `tipo` ∈ negativa | keyword |
titulo | descripcion | grupo | texto; `destino` = «Toda la campaña», «Grupo «X»», «Anuncio id N · grupo «X»»,
«Anuncio nuevo · grupo «X»», «La campaña», «Configuración de la campaña › …». Un paso de anuncio lista cada reemplazo
(item con `reemplaza`). Un paso de grupo nuevo lista: crear grupo (motivo con la URL final), sus keywords y su anuncio.
Si una tarjeta propone una campaña nueva, `campana` = null, `campanas` = ["<nombre propuesto> (campaña nueva, a crear)"],
y los pasos dicen configuración concreta (presupuesto diario en ARS y de dónde sale, estrategia, ubicación, idioma,
grupos, keywords, negativas iniciales, URL final, anuncio).

## Formato SEO (ficha «seo»)

```json
{"tarjetas": [{
  "clave": "clave existente", "marca": "CU|PS", "sitio": "espana.controlunion.com",
  "titulo": "≤ 140 caracteres, sin «…»", "detalle": "2–4 frases", "prioridad": "alta|media|baja",
  "evidencia": {
    "ficha": "seo", "sitio": "espana.controlunion.com",
    "paginas": [{"url": "https://…", "nota": "la que se cambia / la que se redirige / …"}],
    "acciones": ["contenido","tecnico","landing","revisar"],
    "resumen": "…", "por_que": "queries, impresiones, posición, CTR, período (Search Console)", "ya_hecho": "…",
    "pasos": [{"accion": "contenido", "titulo": "Reescribir el title y la meta description", "donde": "https://…",
               "detalle": "…", "items": [
        {"accion": "reemplazar", "tipo": "title", "texto": "Certificación GRS en España | Control Union",
         "reemplaza": "<title actual, copiado de la página>", "destino": "https://…", "motivo": "…"},
        {"accion": "redirigir", "tipo": "url", "texto": "301 → https://…/iscc/", "destino": "https://…/iscc_eu/", "motivo": "…"}]}],
    "organico": [{"query","impr","pos"}], "organico_desde": "España", "organico_hasta": "14 sep 2026",
    "datos_hasta": "14 sep 2026 (Search Console); páginas leídas el 28 oct 2026"}}],
 "descartes": [{"clave","motivo"}]}
```

SEO items: `tipo` ∈ title (≤ 60) | meta (≤ 155) | h1 (≤ 70) | url | texto (secciones, enlaces internos con su anchor
y la página de origen, hreflang/canonical con el valor exacto); `accion` ∈ reemplazar | agregar | crear | redirigir |
editar | decidir. Enlaces internos: item por enlace («desde URL A, anchor "…", hacia URL B»). Contenido nuevo: el H2 de
cada sección y en una línea qué dice. Lo que depende del CMS o de alguien de la unidad se dice («pedir a …»).

## Antes de entregar

`python proyecto/scripts/chequear_lote.py <tu archivo>` tiene que dar 0 errores. Arreglá y volvé a correr.
Tu respuesta final: 5–10 líneas con qué tarjetas reescribiste, cuáles unificaste o descartaste y por qué, y cualquier
dato que no pudiste verificar.
