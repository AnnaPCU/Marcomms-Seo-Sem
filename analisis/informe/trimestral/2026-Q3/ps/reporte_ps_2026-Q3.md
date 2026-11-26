# Peterson Solutions — datos del reporte trimestral 2026-Q3
Período: 01/07/2026 al 30/09/2026 (trimestre calendario completo). Fuentes: Google Search Console (hoja SEO) y Google Analytics 4 (hoja Website). Extraído el 09/10/2026.

Dónde va cada dato en el reporte (una cuenta / región por reporte):

- Hoja **SEO**: «SEO — 2026-Q3» = Average Position, Impressions, Total Clicks · «Embudo de búsqueda — Impresión → Clic» = Impressions → Total Clicks con el CTR · «Top keywords — clics» = lista de keywords · «Generals KPIs» = gráfico de barras con Avg. Position, Impressions y Total Clicks.
- Hoja **Website**: «Website — 2026-Q3» = Single Traffic, Total Traffic, Impressions, Conversions · «Embudo de tráfico — Vista → Sesión → Conversión» = vistas → sesiones → conversiones con sus % · «Top landing pages — vistas» = lista de páginas · «Generals KPIs» = gráfico de barras con Single Traffic, Total Traffic, Impressions y Conversions.
- No incluido (lo completa el creador del reporte): insights y plan de acción, diagnóstico, próximos pasos, glosario y el casillero «Deals generados — HubSpot».

### Qué cuenta como «Conversions»

Conversions = **formularios + emails**: alguien completó un formulario o hizo clic en un email (mailto).

- **Formularios**: todo formulario del sitio, de Gravity Forms o de HubSpot, redirige al enviarse a una página de gracias (gracias / thank-you / obrigado / agradecemos). Se cuentan las vistas a esas páginas **cuando se llegó desde otra página del mismo sitio**, que es como se ve un envío. Las entradas directas sin página de origen (revisiones del equipo y robots, ~60 % de las vistas a esas páginas en el 3T 2026) quedan afuera, igual que las que vienen del administrador del sitio, de empleo, academy o reclamos.
- **Emails**: evento click_email, salvo los que salen de páginas de empleo (vacantes, vagas, carreiras, careers), de la academia de cursos (academy) y de reclamos.

No se usa el evento form_submit: además de formularios registraba el buscador del sitio y el acceso de administración (/exp-admin), y no ve los formularios de HubSpot (van dentro de un iframe).

Límites: la página de gracias cuenta vistas, no envíos únicos (si alguien la recarga, suma dos), y si el navegador no informa la página de origen el envío no se cuenta. La columna «todas las vistas» muestra el techo sin filtrar. La pestaña «Sitios · GA4» del tablero todavía cuenta los formularios con form_submit «gform_» y no suma las páginas de gracias.

Hasta el 9 oct 2026 este reporte sumaba click_email + form_submit en crudo, lo que inflaba la cifra. Comparación por sitio:

| Cuenta | form_submit (crudo) | click_email (crudo) | Antes | Páginas de gracias (todas las vistas) | Formularios (página de gracias, filtrado) | Emails reales | Ahora |
|---|---:|---:|---:|---:|---:|---:|---:|
| Peterson Solutions South America | 27 | 0 | 27 | 14 | 6 | 0 | 6 |
| Peterson Solutions Iberia | 24 | 0 | 24 | 17 | 3 | 0 | 3 |
| **Total** | **51** | **0** | **51** | **31** | **9** | **0** | **9** |

## Peterson Solutions South America

### SEO — Search Console

| Average Position | Impressions | Total Clicks | CTR (impresión → clic) |
|---:|---:|---:|---:|
| 10,06 | 26.163 | 486 | 1,86 % |

Top keywords por clics:

1. peterson solutions — 116
2. peterson solutions brasil — 31
3. peterson — 15
4. peterson projects and solutions — 3
5. peterson solution — 3

### Website — Google Analytics 4

| Single Traffic | Total Traffic | Impressions | Conversions |
|---:|---:|---:|---:|
| 1.421 | 1.861 | 3.414 | 6 |

Conversions = formularios por página de gracias (6) + emails (0). Con la definición anterior (click_email + form_submit en crudo) daba 27.
Embudo: vistas 3.414 → sesiones 1.861 (54,51 %) → conversiones 6 (0,32 % de las sesiones).

Top páginas por vistas:

1. https://americas.peterson-solutions.com/ — 368
2. https://americas.peterson-solutions.com/service/sostenibilidad-en-la-cadena-de-suministro/agricultura-regenerativa/ — 301
3. https://americas.peterson-solutions.com/pt-br/ — 246
4. https://americas.peterson-solutions.com/en/privacy-policy/ — 194
5. https://americas.peterson-solutions.com/service/estrategia-y-gestion-de-sostenibilidad/gei-y-servicios-medioambientales/ — 127

## Peterson Solutions Iberia

### SEO — Search Console

| Average Position | Impressions | Total Clicks | CTR (impresión → clic) |
|---:|---:|---:|---:|
| 10,53 | 17.478 | 389 | 2,23 % |

Top keywords por clics:

1. peterson solutions — 102
2. peterson solutions iberia — 30
3. one peterson — 4
4. peterson's solution — 3
5. ecgt — 2

### Website — Google Analytics 4

| Single Traffic | Total Traffic | Impressions | Conversions |
|---:|---:|---:|---:|
| 476 | 702 | 1.452 | 3 |

Conversions = formularios por página de gracias (3) + emails (0). Con la definición anterior (click_email + form_submit en crudo) daba 24.
Embudo: vistas 1.452 → sesiones 702 (48,35 %) → conversiones 3 (0,43 % de las sesiones).

Top páginas por vistas:

1. https://iberia.peterson-solutions.com/ — 219
2. https://iberia.peterson-solutions.com/service/estrategia-y-gestion-de-sostenibilidad/eu-green-consumer-directive-ecgt-compliance/ — 57
3. https://iberia.peterson-solutions.com/eudr/ — 51
4. https://iberia.peterson-solutions.com/packaging-and-packaging-waste-regulation-ppwr/ — 51
5. https://iberia.peterson-solutions.com/vacantes/ — 49
