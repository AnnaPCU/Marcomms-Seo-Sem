# Control Union — datos del reporte trimestral 2026-Q3
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
| Control Union Argentina | 65 | 153 | 218 | 95 | 19 | 13 | 32 |
| Control Union Brasil | 63 | 234 | 297 | 76 | 53 | 132 | 185 |
| Control Union Chile | 33 | 71 | 104 | 40 | 15 | 33 | 48 |
| Control Union España | 41 | 28 | 69 | 70 | 19 | 18 | 37 |
| Control Union México | 26 | 95 | 121 | 58 | 39 | 47 | 86 |
| Control Union North America | 102 | 78 | 180 | 57 | 35 | 27 | 62 |
| Control Union Perú | 110 | 155 | 265 | 49 | 21 | 86 | 107 |
| Control Union Portugal | 37 | 54 | 91 | 30 | 7 | 36 | 43 |
| **Total** | **477** | **868** | **1.345** | **475** | **208** | **392** | **600** |

## Control Union Argentina

### SEO — Search Console

| Average Position | Impressions | Total Clicks | CTR (impresión → clic) |
|---:|---:|---:|---:|
| 9,11 | 76.744 | 1.855 | 2,42 % |

Top keywords por clics:

1. control union — 489
2. control union argentina — 181
3. control union argentina s.a — 30
4. control union tucuman — 29
5. visec — 26

### Website — Google Analytics 4

| Single Traffic | Total Traffic | Impressions | Conversions |
|---:|---:|---:|---:|
| 2.920 | 4.098 | 8.566 | 32 |

Conversions = formularios por página de gracias (19) + emails (13). Con la definición anterior (click_email + form_submit en crudo) daba 218.
Embudo: vistas 8.566 → sesiones 4.098 (47,84 %) → conversiones 32 (0,78 % de las sesiones).

Top páginas por vistas:

1. https://argentina.controlunion.com/ — 1.545
2. https://argentina.controlunion.com/nosotros/ — 552
3. https://argentina.controlunion.com/vacantes/ — 512
4. https://argentina.controlunion.com/programas-de-certificacion/ — 429
5. https://argentina.controlunion.com/contacto/ — 310

## Control Union Brasil

### SEO — Search Console

| Average Position | Impressions | Total Clicks | CTR (impresión → clic) |
|---:|---:|---:|---:|
| 10,49 | 62.175 | 1.874 | 3,01 % |

Top keywords por clics:

1. control union — 689
2. controlunion — 117
3. control union brasil — 77
4. control union latinoamérica — 52
5. control union warrants ltda — 50

### Website — Google Analytics 4

| Single Traffic | Total Traffic | Impressions | Conversions |
|---:|---:|---:|---:|
| 3.040 | 3.793 | 7.258 | 185 |

Conversions = formularios por página de gracias (53) + emails (132). Con la definición anterior (click_email + form_submit en crudo) daba 297.
Embudo: vistas 7.258 → sesiones 3.793 (52,26 %) → conversiones 185 (4,88 % de las sesiones).

Top páginas por vistas:

1. https://brasil.controlunion.com/ — 2.288
2. https://brasil.controlunion.com/contato/ — 576
3. https://brasil.controlunion.com/vagas/ — 496
4. https://brasil.controlunion.com/programas-de-certificacao/ — 413
5. https://brasil.controlunion.com/quem-somos/ — 352

## Control Union Chile

### SEO — Search Console

| Average Position | Impressions | Total Clicks | CTR (impresión → clic) |
|---:|---:|---:|---:|
| 11,3 | 29.122 | 463 | 1,59 % |

Top keywords por clics:

1. control union — 69
2. control union chile — 51
3. grasp — 11
4. bap — 10
5. controlunion — 8

### Website — Google Analytics 4

| Single Traffic | Total Traffic | Impressions | Conversions |
|---:|---:|---:|---:|
| 957 | 1.197 | 2.628 | 48 |

Conversions = formularios por página de gracias (15) + emails (33). Con la definición anterior (click_email + form_submit en crudo) daba 104.
Embudo: vistas 2.628 → sesiones 1.197 (45,55 %) → conversiones 48 (4,01 % de las sesiones).

Top páginas por vistas:

1. https://chile.controlunion.com/ — 490
2. https://chile.controlunion.com/programas-de-certificacion/ — 209
3. https://chile.controlunion.com/contacto/ — 122
4. https://chile.controlunion.com/service/certificaciones/ — 114
5. https://chile.controlunion.com/nosotros/ — 87

## Control Union España

### SEO — Search Console

| Average Position | Impressions | Total Clicks | CTR (impresión → clic) |
|---:|---:|---:|---:|
| 14,11 | 171.269 | 1.393 | 0,81 % |

Top keywords por clics:

1. control union — 221
2. control union españa — 48
3. controlunion — 39
4. iso 21401 — 22
5. sure — 11

### Website — Google Analytics 4

| Single Traffic | Total Traffic | Impressions | Conversions |
|---:|---:|---:|---:|
| 2.370 | 2.798 | 5.961 | 37 |

Conversions = formularios por página de gracias (19) + emails (18). Con la definición anterior (click_email + form_submit en crudo) daba 69.
Embudo: vistas 5.961 → sesiones 2.798 (46,94 %) → conversiones 37 (1,32 % de las sesiones).

Top páginas por vistas:

1. https://espana.controlunion.com/ — 518
2. https://espana.controlunion.com/programa-de-certificacion/certification-program-iso-27001-certification/ — 393
3. https://espana.controlunion.com/programas-de-certificacion/ — 270
4. https://espana.controlunion.com/programa-de-certificacion/iso-9001/ — 237
5. https://espana.controlunion.com/contacto/ — 174

## Control Union México

### SEO — Search Console

| Average Position | Impressions | Total Clicks | CTR (impresión → clic) |
|---:|---:|---:|---:|
| 11,46 | 59.107 | 738 | 1,25 % |

Top keywords por clics:

1. control union — 114
2. control union mexico — 63
3. controlunion — 8
4. organico mexico — 8
5. grs — 7

### Website — Google Analytics 4

| Single Traffic | Total Traffic | Impressions | Conversions |
|---:|---:|---:|---:|
| 2.092 | 2.493 | 4.445 | 86 |

Conversions = formularios por página de gracias (39) + emails (47). Con la definición anterior (click_email + form_submit en crudo) daba 121.
Embudo: vistas 4.445 → sesiones 2.493 (56,09 %) → conversiones 86 (3,45 % de las sesiones).

Top páginas por vistas:

1. https://mexico.controlunion.com/ — 1.379
2. https://mexico.controlunion.com/contacto-mexico/ — 284
3. https://mexico.controlunion.com/programas-de-certificacion/ — 221
4. https://mexico.controlunion.com/service/certificaciones/ — 154
5. https://mexico.controlunion.com/nosotros/ — 141

## Control Union North America

### SEO — Search Console

| Average Position | Impressions | Total Clicks | CTR (impresión → clic) |
|---:|---:|---:|---:|
| 14,63 | 30.970 | 313 | 1,01 % |

Top keywords por clics:

1. control union canada — 37
2. control union usa — 29
3. control union — 17
4. temo — 2
5. control union job vacancy — 1

### Website — Google Analytics 4

| Single Traffic | Total Traffic | Impressions | Conversions |
|---:|---:|---:|---:|
| 2.475 | 3.200 | 6.388 | 62 |

Conversions = formularios por página de gracias (35) + emails (27). Con la definición anterior (click_email + form_submit en crudo) daba 180.
Embudo: vistas 6.388 → sesiones 3.200 (50,09 %) → conversiones 62 (1,94 % de las sesiones).

Top páginas por vistas:

1. https://northamerica.controlunion.com/ — 1.474
2. https://northamerica.controlunion.com/certification-programs/ — 600
3. https://northamerica.controlunion.com/vacancies/ — 296
4. https://northamerica.controlunion.com/contact/ — 289
5. https://northamerica.controlunion.com/service/certification/ — 218

## Control Union Perú

### SEO — Search Console

| Average Position | Impressions | Total Clicks | CTR (impresión → clic) |
|---:|---:|---:|---:|
| 7,83 | 274.322 | 3.993 | 1,46 % |

Top keywords por clics:

1. control union — 393
2. control union peru — 182
3. control union services — 175
4. control union services s.a.c — 43
5. smeta 7.0 standard pdf — 41

### Website — Google Analytics 4

| Single Traffic | Total Traffic | Impressions | Conversions |
|---:|---:|---:|---:|
| 4.080 | 6.009 | 11.431 | 107 |

Conversions = formularios por página de gracias (21) + emails (86). Con la definición anterior (click_email + form_submit en crudo) daba 265.
Embudo: vistas 11.431 → sesiones 6.009 (52,57 %) → conversiones 107 (1,78 % de las sesiones).

Top páginas por vistas:

1. https://peru.controlunion.com/ — 2.585
2. https://peru.controlunion.com/programas-de-certificacion/ — 572
3. https://peru.controlunion.com/service/certificaciones/ — 466
4. https://peru.controlunion.com/vacantes/ — 440
5. https://peru.controlunion.com/nosotros/ — 406

## Control Union Portugal

### SEO — Search Console

| Average Position | Impressions | Total Clicks | CTR (impresión → clic) |
|---:|---:|---:|---:|
| 14,4 | 46.940 | 692 | 1,47 % |

Top keywords por clics:

1. control union — 144
2. control union portugal — 58
3. controlunion — 28
4. grs — 28
5. gots — 8

### Website — Google Analytics 4

| Single Traffic | Total Traffic | Impressions | Conversions |
|---:|---:|---:|---:|
| 1.525 | 1.686 | 3.456 | 43 |

Conversions = formularios por página de gracias (7) + emails (36). Con la definición anterior (click_email + form_submit en crudo) daba 91.
Embudo: vistas 3.456 → sesiones 1.686 (48,78 %) → conversiones 43 (2,55 % de las sesiones).

Top páginas por vistas:

1. https://portugal.controlunion.com/ — 663
2. https://portugal.controlunion.com/esquemas-de-certificacao/ — 156
3. https://portugal.controlunion.com/contacto/ — 132
4. https://portugal.controlunion.com/certificacoes/ — 89
5. https://portugal.controlunion.com/quem-somos/ — 66
