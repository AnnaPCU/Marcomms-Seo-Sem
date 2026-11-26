# Contexto — Conversiones GA4 en los reportes trimestrales MarComms

Traspaso de la conversación del 9 oct 2026 (validación GA4 para el reporte trimestral y el tablero Marcomms SEO-SEM).
Pieza interna: cubre las dos marcas, pero los datos siguen en archivos separados por marca.

---

## 1. Definición final de «Conversions» (decidida por Felipe el 9 oct 2026)

**Conversiones = formularios (vistas a páginas de gracias) + clics a email (mailto).**

- **Formularios**: todo formulario del sitio, sea de Gravity Forms o de HubSpot (que va en un iframe), redirige al enviarse a una
  página de gracias. Se cuentan las **vistas a esas páginas** (pagePath que contiene thank / gracias / obrigad / agradec)
  **solo si se llegó desde otra página del mismo sitio** (pageReferrer empieza con `https://<host>/`).
  Se descartan:
  - entradas directas sin página de origen (revisiones del equipo y robots, ~60 % de las vistas en el 3T 2026);
  - orígenes de administración (wp-admin, wp-login, exp-admin);
  - orígenes que son otra página de gracias;
  - orígenes de empleo, academy o reclamos.
- **Emails**: evento `click_email`, salvo los que salen de páginas de empleo (vacantes, vagas, carreiras, careers),
  de la academia (academy) o de reclamos.
- **Ya no se usa `form_submit`**: registraba el buscador del sitio y el login de /exp-admin, y no ve los formularios de HubSpot.

Límites que hay que declarar:
- Cuenta vistas, no envíos únicos: si alguien recarga la página de gracias, suma dos.
- Si el navegador no informa la página de origen, el envío no se cuenta, así que el número tiende a quedarse corto.
- El reporte incluye la columna «todas las vistas» a páginas de gracias como techo sin filtrar.
- El total exacto de HubSpot se confirma en HubSpot.

## 2. Números del 3T 2026 (jul–sep, extraídos el 9 oct 2026)

### Control Union

| Sitio | Antes (crudo) | Gracias, todas las vistas | Formularios (filtrado) | Emails | **Conversiones** |
|---|---:|---:|---:|---:|---:|
| Argentina | 218 | 95 | 19 | 13 | **32** |
| Brasil | 297 | 76 | 53 | 132 | **185** |
| Chile | 104 | 40 | 15 | 33 | **48** |
| España | 69 | 70 | 19 | 18 | **37** |
| México | 121 | 58 | 39 | 47 | **86** |
| North America | 180 | 57 | 35 | 27 | **62** |
| Perú | 265 | 49 | 21 | 86 | **107** |
| Portugal | 91 | 30 | 7 | 36 | **43** |
| **Total** | **1.345** | **475** | **208** | **392** | **600** |

North America por país: Estados Unidos 96 → **47** (25 formularios + 22 emails) · Canadá 4 → **6** (3 + 3).

### Peterson Solutions

| Sitio | Antes (crudo) | Gracias, todas las vistas | Formularios (filtrado) | Emails | **Conversiones** |
|---|---:|---:|---:|---:|---:|
| South America | 27 | 14 | 6 | 0 | **6** |
| Iberia | 24 | 17 | 3 | 0 | **3** |
| **Total** | **51** | **31** | **9** | **0** | **9** |

«Antes» = click_email + form_submit en crudo, la definición que usaba el reporte hasta el 9 oct 2026.

## 3. Hallazgos verificados contra la API

- **form_submit estaba inflado.** En el 3T hubo 528 eventos:
  - 318 del buscador del sitio (form_id «searchform»);
  - 199 del login de /exp-admin;
  - 7 formularios reales de Gravity (`gform_`: 1 de CU España y 6 de PS Iberia);
  - 4 sin form_id: /carreiras/ (2), /cis-login/ (1) y /en/careers/ (1).

  El «11 formularios reales» que circulaba era el resto de 528 − 318 − 199: incluía esos 4 de empleo y login.
- **click_email salía sobre todo de páginas de vacantes, carreiras, academy y reclamos.** En los sitios de Peterson
  click_email da 0 en el 3T.
- **Las vistas directas a las páginas de gracias no son envíos.** Argentina tiene más de 15 variantes de página de gracias
  con 2 vistas directas desde Argentina y 1 desde Alemania o China cada una. El 7 sep 2026 alguien abrió todas las páginas
  de gracias de PS Iberia de una vez. Los envíos reales llegan desde /contacto/, /contato/, /contact/ o las páginas de servicio.
- **Gravity Forms también redirige a la página de gracias.** En PS Iberia, gform_11 en /eudr/ (3 envíos, 2 y 3 de julio)
  coincide con 2 vistas a /gracias-eudr/ que llegan desde /eudr/ esos mismos días.
- **Excepción sin confirmar: PS Iberia gform_15 en la portada.** Tuvo 3 envíos el 2 y 3 de julio y ninguna vista a una
  página de gracias en esos días. No redirige: puede ser un newsletter o envíos de prueba. Por eso Iberia quedó en 3.
  **Pendiente confirmarlo con quien maneja el sitio.**
- **Brasil** casi no tenía formularios medidos y ahora suma 53, la mayoría desde /contato/.
- Felipe **no tiene acceso a Google Tag Manager**, así que no se puede agregar un evento de envío de HubSpot. Por eso se
  usan las páginas de gracias.

## 4. Archivos y cómo se corre

- `proyecto/scripts/reporte_trimestral.py AAAA-QN` → `informe/trimestral/<AAAA-QN>/<cu|ps>/reporte_<marca>_<AAAA-QN>.json/.md`
- `proyecto/scripts/reporte_trimestral.py AAAA-QN --paises` → `cu/reporte_cu_<AAAA-QN>_northamerica_por_pais.json/.md`
- Accesos: `token.json` (Search Console) y `token_ga4.json` (GA4), los dos de tmisrahi@onepeterson.com, solo lectura.
- Las definiciones viven en **`proyecto/scripts/ga4_export.py`** y el reporte las importa, sin copiarlas:
  - `gracias_real(host)`: formularios por página de gracias (usa `PAGINA_GRACIAS`, `GRACIAS` y `REF_DESCARTE`).
  - `EMAIL_REAL`: clics a email sin empleo, academy ni reclamos (regex `EMPLEO`).
  - `FORM_REAL`: form_submit con form_id `gform_`. **Solo lo usa el tablero**; el reporte ya no.
- Cada `.md` incluye:
  - la sección «Qué cuenta como Conversions»;
  - los límites de la medición;
  - la tabla antes/después por sitio, con columnas form_submit crudo | click_email crudo | Antes | Gracias, todas las vistas | Formularios filtrados | Emails | Ahora.
- El JSON trae:
  - `conversions_detalle` = {formularios, emails};
  - `conversions_crudas` = {click_email, form_submit, total};
  - `vistas_gracias_sin_filtro`;
  - `definicion_conversion`.

Detalles técnicos:
- **Importación circular.** `ga4_export.py` importa `PROPIEDADES` de `reporte_trimestral.py`. Por eso
  `reporte_trimestral.py` importa de `ga4_export` dentro de `website()`; una importación al principio del archivo fallaría.
- **Filtros de la GA4 Data API.** Se pueden anidar `andGroup` y `notExpression`. El filtro por país (`countryId`) se combina
  con AND sobre cada filtro.

## 5. Pendientes

1. **El tablero no coincide con el reporte.** La pestaña «Sitios · GA4» (`ga4_export.py`, `sitio_mes()`) todavía cuenta
   los formularios con `FORM_REAL` y no con las páginas de gracias, así que muestra otros números. Quedó una propuesta de
   sesión para alinearlo («Alinear la pestaña Sitios · GA4 con páginas de gracias»). Criterio de listo: la suma jul+ago+sep
   por sitio coincide con la columna «Ahora» (CU 600, PS 9). Mientras tanto, no se tocó el tablero web.
2. **Confirmar** si gform_15 de la portada de PS Iberia es un newsletter o envíos de prueba.
3. **Decisión abierta: filtrar o no las vistas.** Hoy se filtran por página de origen. Si Felipe prefiere contar todas
   las vistas a páginas de gracias, el número de formularios pasa a ser la columna «todas las vistas» (CU 475, PS 31).
   Se cambia en una línea.
4. **Decisión tomada, revisable: academy afuera.** Los contactos que salen de academy se excluyen en formularios y emails
   por coherencia (Perú 3 y Brasil 1 vistas a páginas de gracias desde academy en el 3T).
5. Q1 y Q2 2026 no se rehacen, por decisión de Felipe, aunque no coincidan con la definición nueva.
