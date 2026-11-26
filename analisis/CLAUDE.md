# Inteligencia de búsqueda — Peterson Control Union World Group

Proyecto de análisis cruzado entre **Google Ads** y **Google Search Console** para las
campañas y sitios del grupo. Este archivo es el brief maestro: leelo completo antes de
hacer nada.

**Dónde vive (desde el 26 nov 2026):** en `analisis/` del repo AnnaPCU/Marcomms-Seo-Sem, junto al tablero. En la
compu de Felipe se sigue abriendo como `Optimizaciónes SEO-SEM/proyecto` (es un acceso directo a esa carpeta).
También se puede trabajar en una **sesión en la nube** (claude.ai/code, entorno «SEO-SEM»), que no depende de que la
compu esté prendida: ver `nube/LEEME.md`. En la nube no está la memoria de Claude de la compu; su equivalente es
`docs/memoria/` (empezá por `INDICE.md`), y lo nuevo que valga para próximas sesiones se anota ahí.

Responsable: Felipe Señorans, Marketing Campaign Specialist. Escribe y piensa en español
rioplatense; los entregables para cliente van en inglés.

---

## 1. Regla de marca — no negociable

**Control Union y Peterson Solutions son dos marcas separadas y NUNCA se mezclan.**
Ni en un archivo, ni en una pieza, ni en una paleta, ni en un informe con identidad de marca.

| | Control Union | Peterson Solutions |
|---|---|---|
| Qué es | Organismo certificador acreditado | Consultora |
| Dice | certificamos, auditamos, inspeccionamos, verificamos | acompañamos, co-desarrollamos, preparamos para certificar |
| **Nunca dice** | «asesoramos», «diseñamos tu estrategia» (conflicto de interés) | «certificamos» (no emite certificados) |
| Color | Cyan `#3eb2ed` + Grey `#799495` | Dark Blue `#1b1e42` + Aqua `#44cbce` + Yellow `#f1e747` |
| Tipografía | Sansa Pro / Ubuntu / Calibri | Sansa Soft / Ubuntu / Calibri |
| Dominio | controlunion.com · @controlunion.com | peterson-solutions.com · @onepeterson.com |

Consecuencias prácticas para este proyecto:

- Los datos de las dos marcas se extraen y se guardan en **archivos separados**. Nunca un CSV común.
- Los informes que cubren las dos marcas son **piezas internas sin identidad de marca**:
  paleta limitada a los colores que ambos manuales comparten (Dark Blue `#1b1e42`,
  Dark Grey `#4f6566`, Light Grey `#799495`), tipografía Calibri, sin logos ni taglines.
  Siempre llevan una nota al pie explicando por qué.
- Si un hallazgo es de Peterson, no se resuelve con campañas de Control Union, ni al revés.

---

## 2. Objetivo de este proyecto

Ads dice **qué se compra**. Search Console dice **qué ya se tiene**. Cruzarlos separa tres
cosas que de otro modo se confunden: lo que conviene pagar, lo que conviene escribir, y lo
que no conviene ninguna de las dos.

El objetivo de esta etapa es **reconstruir el histórico completo disponible en GSC (16 meses,
el máximo que Google guarda) y rehacer el análisis sobre esa base**, más rica que la de 12
meses con la que se hizo el informe actual.

Google **borra** los datos de Search Console pasados 16 meses y no hay forma de recuperarlos.
Por eso el archivo histórico local no es una comodidad: es lo único que va a existir cuando
Google descarte esos meses.

---

## 3. Accesos

- **Cuentas** (desde el 5 oct 2026, cada servicio con la suya):
  - Search Console → `tmisrahi@onepeterson.com` (token.json).
  - Google Ads → `tmpcugroup@gmail.com`, la que tiene acceso a la cuenta de Ads (google-ads.yaml).
  - Google Analytics 4 → `tmisrahi@onepeterson.com` (token_ga4.json, solo lectura; desde el 9 oct 2026, `ads_auth.py --ga4`).
  - Meta Ads → token de usuario del sistema (rol Empleado) en `meta-ads.json`, que carga quien administra el portfolio
    (desde el 31 oct 2026; ver `META_ADS.md`). Lectura con `meta_export.py`; subida con `meta_subir.py` o el MCP oficial
    de Meta, siempre en pausa y con un «sí» explícito por acción. Nunca pegar el token en el chat.
  - Supabase (tablero) → por el conector MCP; opcionalmente `supabase-service.json` ({"url", "service_key"}) en esta
    carpeta para que `publicar.py` cargue por REST sin conector. Lo crea el usuario; nunca se muestra ni se pega en el chat.
  - Historial de cambios de Google Ads → `scripts/ads_cambios.py` (change_event, solo lectura, 30 días) para la vista «Impacto».
  Se autoriza con `scripts/ads_auth.py --gsc` / `--ads CUENTA`; el script comprueba la cuenta antes de
  guardar. El proyecto de Google Cloud («GSC Export PCU») está en la organización personal «tmisrahi-org»,
  no en onepeterson.com: por eso «Interno» bloquea a onepeterson y la app tiene que ser «Externa».
- **Credencial**: `client_secret.json` (OAuth de aplicación de escritorio) y `token.json`
  en la carpeta del proyecto. No los subas a ningún lado ni los pegues en un chat.
- **Scope**: `https://www.googleapis.com/auth/webmasters.readonly` — solo lectura.
- **La app está en modo Testing**: el token vence cada 7 días. A cadencia mensual da igual,
  se reautoriza con un clic. **No publiques la app a Producción** sin consultar: dispara
  verificación de Google.
- Niveles de permiso en GSC: *Full* en las propiedades de Control Union, *Restricted* en las
  de Peterson. Restricted alcanza para leer Rendimiento. Felipe **no** puede agregar usuarios
  ni cuentas de servicio — eso requiere Owner.

Cuotas de la API: 1.200 consultas por minuto por sitio, 40.000 por minuto por proyecto.
Una extracción completa usa unas 50. No es un límite relevante.

---

## 4. Las diez propiedades

No existe una propiedad global `controlunion.com`. Son subdominios por país.

| Propiedad | Marca | Campañas de Ads que le corresponden |
|---|---|---|
| `https://espana.controlunion.com/` | CU | CU España — 11 campañas |
| `https://portugal.controlunion.com/` | CU | CU Portugal — 7 |
| `https://northamerica.controlunion.com/` | CU | CU Canadá — 5 (país `can`) · CU Estados Unidos — 2 (país `usa`) |
| `https://argentina.controlunion.com/` | CU | CU Argentina — 2 |
| `https://brasil.controlunion.com/` | CU | ninguna |
| `https://mexico.controlunion.com/` | CU | ninguna |
| `https://chile.controlunion.com/` | CU | ninguna |
| `https://peru.controlunion.com/` | CU | ninguna |
| `https://americas.peterson-solutions.com/` | PS | PS Argentina — 8 (país `arg`) |
| `https://iberia.peterson-solutions.com/` | PS | ninguna |

`northamerica` junta Canadá y Estados Unidos, que son campañas con presupuesto separado:
**el país va como dimensión, no como filtro**, para que se partan solas.

Las propiedades sin campaña se extraen igual: sirven para detectar demanda en mercados donde
todavía no se invierte, y ya demostraron rendir más que las que sí tienen campaña.

---

## 5. Qué pedirle a la API

**Métricas** (son las únicas que existen): `clicks`, `impressions`, `ctr`, `position`.

**Dimensiones a extraer**, por propiedad:

| Corte | Dimensiones | Para qué |
|---|---|---|
| `queries` | query + country + **date** | El cruce contra Ads y la serie temporal |
| `pages` | page + **date** | Autoridad orgánica por página |
| `query_page` | query + page | Qué página rankea para cada búsqueda |
| `devices` | query + **device** | Cuánto es móvil — no se midió nunca |

**`date` y `device` faltaron en la extracción anterior y hay que sumarlos.** Sin `date` no hay
tendencia y no se puede verificar hasta qué día llegó la cobertura real.

**Parámetros**: `type=web`, `dataState=final`, `rowLimit=25000` con paginación por `startRow`.

**Ventana**: la máxima disponible. Arrancá pidiendo desde 16 meses atrás y caminá hacia
adelante hasta que aparezcan datos — la fecha más vieja se corre todos los días.
`dataState=final` descarta los últimos 2 o 3 días.

---

## 6. Los seis cruces

Definiciones exactas. Respetalas para que los números sean comparables mes a mes.

1. **Canibalización** — términos que se pagan y ya rankean en posición 1–3 orgánica.
   En la medición base era ARS 3.594, el 1% del gasto. No es un problema; verificar que siga así.
2. **Zona donde el paid rinde** — posición 8–20: el sitio es relevante pero invisible.
   ARS 106.531 en la base. **Es también la cola de prioridades de SEO, ordenada por plata.**
3. **Huecos de contenido** — términos pagos con clic sobre temas donde el sitio no tiene nada.
   ARS 284.290, el 41% del gasto relevante.
4. **Demanda no comprada** — queries con 40+ impresiones que no existen en la cuenta de Ads,
   ni como keyword ni como término de búsqueda.
5. **Landing desalineada** — la página que rankea orgánicamente ≠ la URL final del anuncio.
6. **Validación de negativos** — antes de negativizar un tema, comprobar si el sitio rankea
   para él. Si rankea, probablemente hay servicio y el negativo está mal.

**Regla metodológica crítica:** el cruce por coincidencia exacta de string da 91% de «sin
presencia» y **es falso** — `pefc españa` no figura en GSC pero `pefc` sí, con 428 impresiones.
Todos los números se calculan por **coincidencia de tema** (tokens de 3+ caracteres, sin
stopwords ni palabras genéricas como «certificación» o «auditoría»), que da 41% y es defendible.

---

## 7. Estado: qué ya está decidido

No vuelvas a litigar esto salvo que los datos nuevos lo contradigan.

**Resuelto con evidencia:**

- **FSC en España y Portugal**: las dos filiales **sí certifican** — tienen página de programa
  de certificación propia y 4.149 impresiones anuales. El negativo que proponía la auditoría de
  Ads **era incorrecto** y fue corregido. Corresponde abrir grupo de anuncios.
- **OEKO-TEX en Textile España**: **cero apariciones** en 20.561 queries de doce meses.
  Control Union no lo certifica. Negativo confirmado. ARS 15.362 recuperables.
- **ISO 22000 y FSSC 22000 en España**: tienen página y demanda (2.235 y 708 impresiones).
  Merecen grupo propio. **BRCGS no**: 33 impresiones en un año, va a negativo.
- **GMP+ España y Portugal**: la auditoría de Ads decía «no existe operativamente». Falso:
  2.848 impresiones orgánicas en posición 11. El problema era el vocabulario de las keywords.
- **CU Canadá**: 223 impresiones de FSC en doce meses. No hay contenido que sostenga la
  campaña más cara de la cuenta. Forestry y Aqua se pausan.

**Abierto, y no se contesta con estos datos:**

- Si se pausan las campañas de Bioenergía PS y CeSu de Peterson Argentina.
- El corte de marca CU / PS en ISCC Argentina — las dos marcas competirían en la misma subasta.

---

## 8. El informe

Mismo sistema visual que los dos informes anteriores, que están en `referencia/`.
`style.css` y `render.py` son los archivos reales que los generaron.

- A4, grilla de 12 columnas, márgenes 16–17 mm
- Paleta neutra interna: `#1b1e42`, `#4f6566`, `#799495`, tinte `#f3f5f6`
- **Nunca** Cyan `#3eb2ed`, Aqua `#44cbce` ni Yellow `#f1e747` — identifican a una marca
- Calibri / Carlito
- Se renderiza con Playwright + Chromium a PDF, con pie de página numerado

El motor de documentos de Claude no aplica colores de marca al PDF: por eso se maqueta en
HTML y se renderiza con Chromium. No intentes el otro camino, ya se probó.

**Auditá el PDF final**: contá píxeles de los tres colores prohibidos y confirmá que da cero.

---

## 9. Disciplina de verificación

Felipe pide explícitamente que **no se den por ciertas ni sus afirmaciones ni tus conclusiones**
cuando son verificables. Aplica a hechos chequeables, no a opiniones.

- Si él afirma algo verificable («ya subí el archivo», «es la versión final»), **chequealo contra
  la evidencia real antes de responder**. Si se confirma, decilo explícito. Si no, decíselo con
  claridad y proponé el camino más corto — puede haberse confundido de entorno.
- Antes de entregar: **volvé a correr** toda comparación, cálculo o afirmación técnica contra los
  datos fuente. No confíes en la primera pasada.
- Lo que quedó como supuesto sin poder verificarse, **decilo** en vez de presentarlo con la misma
  certeza que lo verificado.
- Cuando te equivoques, **decilo de frente y corregí**. Ya pasó una vez en este proyecto: la
  recomendación de negativizar FSC era incorrecta y el informe nuevo la corrige de forma explícita.

En el informe anterior el chequeo final fue un script que reverificaba los 13 números principales
contra los CSV originales. Hacé lo mismo.

---

## 10. Límites de los datos — declararlos siempre

Ninguna conclusión puede ignorarlos, y el informe los explicita en una sección propia.

- **GSC anonimiza** queries de bajo volumen por umbral de privacidad. No se recuperan.
- **Ads esconde el 43%** del tráfico bajo «Otros términos de búsqueda», y **ahí cayeron las 4
  conversiones del período**. No se puede atribuir conversión a término.
- Las dos fuentes recortan por abajo y del mismo lado: **sirven para decidir dirección, nunca
  para sumar entre sí**.
- **La posición media engaña**: es un promedio de todas las apariciones. Posición 13 puede ser
  mitad en 4 y mitad en 22. Usala como banda, no como número fino.
- Con 4 conversiones en seis semanas **no hay base estadística** para optimizar por CPA.
  Todas las decisiones se apoyan en relevancia de intención.

---

## 11. Qué NO hacer

- No mezclar las dos marcas en un archivo, una paleta o una pieza.
- No publicar la app OAuth a Producción sin consultar.
- No subir `client_secret.json` ni `token.json` a ningún lado.
- No reescribir las conclusiones ya resueltas de la sección 7 salvo que los datos nuevos las
  contradigan — y si lo hacen, decirlo explícitamente.
- No usar coincidencia exacta de string para medir cobertura orgánica.
- No presentar como verificado algo que quedó en supuesto.
