# Control Union North America por país — datos del reporte trimestral 2026-Q3
Período: 01/07/2026 al 30/09/2026 (trimestre calendario completo). Fuentes: Google Search Console (hoja SEO) y Google Analytics 4 (hoja Website). Extraído el 09/10/2026.

Dónde va cada dato en el reporte (una cuenta / región por reporte):

- Hoja **SEO**: «SEO — 2026-Q3» = Average Position, Impressions, Total Clicks · «Embudo de búsqueda — Impresión → Clic» = Impressions → Total Clicks con el CTR · «Top keywords — clics» = lista de keywords · «Generals KPIs» = gráfico de barras con Avg. Position, Impressions y Total Clicks.
- Hoja **Website**: «Website — 2026-Q3» = Single Traffic, Total Traffic, Impressions, Conversions · «Embudo de tráfico — Vista → Sesión → Conversión» = vistas → sesiones → conversiones con sus % · «Top landing pages — vistas» = lista de páginas · «Generals KPIs» = gráfico de barras con Single Traffic, Total Traffic, Impressions y Conversions.
- No incluido (lo completa el creador del reporte): insights y plan de acción, diagnóstico, próximos pasos, glosario y el casillero «Deals generados — HubSpot».

**Este archivo separa el sitio northamerica.controlunion.com por país** (Estados Unidos y Canadá), con los mismos datos que el resto de las cuentas. Cada país se arma como un reporte propio.

Estados Unidos + Canadá no suman el total del sitio: el resto del tráfico viene de otros países. Usuarios y posición promedio no se pueden sumar ni restar entre países.

| Métrica | Total sitio | Estados Unidos | Canadá | Otros países |
|---|---:|---:|---:|---:|
| Clics (SEO) | 313 | 93 | 68 | 152 |
| Impresiones (SEO) | 30.970 | 12.043 | 1.503 | 17.424 |
| Sesiones (Website) | 3.200 | 1.480 | 258 | 1.462 |
| Vistas de página (Website) | 6.388 | 2.684 | 502 | 3.202 |
| Conversiones (Website) | 62 | 47 | 6 | 9 |

### Qué cuenta como «Conversions»

Conversions = **formularios + emails**: alguien completó un formulario o hizo clic en un email (mailto).

- **Formularios**: todo formulario del sitio, de Gravity Forms o de HubSpot, redirige al enviarse a una página de gracias (gracias / thank-you / obrigado / agradecemos). Se cuentan las vistas a esas páginas **cuando se llegó desde otra página del mismo sitio**, que es como se ve un envío. Las entradas directas sin página de origen (revisiones del equipo y robots, ~60 % de las vistas a esas páginas en el 3T 2026) quedan afuera, igual que las que vienen del administrador del sitio, de empleo, academy o reclamos.
- **Emails**: evento click_email, salvo los que salen de páginas de empleo (vacantes, vagas, carreiras, careers), de la academia de cursos (academy) y de reclamos.

No se usa el evento form_submit: además de formularios registraba el buscador del sitio y el acceso de administración (/exp-admin), y no ve los formularios de HubSpot (van dentro de un iframe).

Límites: la página de gracias cuenta vistas, no envíos únicos (si alguien la recarga, suma dos), y si el navegador no informa la página de origen el envío no se cuenta. La columna «todas las vistas» muestra el techo sin filtrar. La pestaña «Sitios · GA4» del tablero todavía cuenta los formularios con form_submit «gform_» y no suma las páginas de gracias.

Hasta el 9 oct 2026 este reporte sumaba click_email + form_submit en crudo, lo que inflaba la cifra. Comparación por sitio:

| Cuenta | form_submit (crudo) | click_email (crudo) | Antes | Páginas de gracias (todas las vistas) | Formularios (página de gracias, filtrado) | Emails reales | Ahora |
|---|---:|---:|---:|---:|---:|---:|---:|
| Control Union North America — Estados Unidos | 29 | 67 | 96 | 30 | 25 | 22 | 47 |
| Control Union North America — Canadá | 0 | 4 | 4 | 3 | 3 | 3 | 6 |
| **Total** | **29** | **71** | **100** | **33** | **28** | **25** | **53** |

## Control Union North America — Estados Unidos

### SEO — Search Console

| Average Position | Impressions | Total Clicks | CTR (impresión → clic) |
|---:|---:|---:|---:|
| 15,95 | 12.043 | 93 | 0,77 % |

Top keywords por clics:

1. control union usa — 16
2. control union — 5
3. control union canada — 1
4. control union organic certification — 1
5. controlunion — 1

### Website — Google Analytics 4

| Single Traffic | Total Traffic | Impressions | Conversions |
|---:|---:|---:|---:|
| 1.192 | 1.480 | 2.684 | 47 |

Conversions = formularios por página de gracias (25) + emails (22). Con la definición anterior (click_email + form_submit en crudo) daba 96.
Embudo: vistas 2.684 → sesiones 1.480 (55,14 %) → conversiones 47 (3,18 % de las sesiones).

Top páginas por vistas:

1. https://northamerica.controlunion.com/ — 706
2. https://northamerica.controlunion.com/certification-programs/ — 343
3. https://northamerica.controlunion.com/vacancies/ — 183
4. https://northamerica.controlunion.com/service/certification/ — 146
5. https://northamerica.controlunion.com/contact/ — 135

## Control Union North America — Canadá

### SEO — Search Console

| Average Position | Impressions | Total Clicks | CTR (impresión → clic) |
|---:|---:|---:|---:|
| 7,86 | 1.503 | 68 | 4,52 % |

Top keywords por clics:

1. control union canada — 27
2. control union — 11
3. fishers finest — 1
4. 22716 iso — 0
5. 4169777771 — 0

### Website — Google Analytics 4

| Single Traffic | Total Traffic | Impressions | Conversions |
|---:|---:|---:|---:|
| 224 | 258 | 502 | 6 |

Conversions = formularios por página de gracias (3) + emails (3). Con la definición anterior (click_email + form_submit en crudo) daba 4.
Embudo: vistas 502 → sesiones 258 (51,39 %) → conversiones 6 (2,33 % de las sesiones).

Top páginas por vistas:

1. https://northamerica.controlunion.com/certification-programs/ — 62
2. https://northamerica.controlunion.com/industry/forestry/ — 56
3. https://northamerica.controlunion.com/ — 48
4. https://northamerica.controlunion.com/vacancies/ — 47
5. https://northamerica.controlunion.com/certification-program/canadagap/ — 40
