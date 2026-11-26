---
name: reportes-trimestrales-gsc-ga4
description: Extracción por API de GSC y GA4 para los reportes trimestrales MarComms (hojas SEO y Website): accesos, definición de Conversions, archivos y pendientes
metadata:
  type: project
---

Acceso por API desde el 9 oct 2026, ambos con tmisrahi@onepeterson.com, solo lectura:
- Search Console: `proyecto/token.json`. GA4: `proyecto/token_ga4.json` (`scripts/ads_auth.py --ga4`; Data + Admin API en
  «GSC Export PCU»; app sin verificar → «Avanzado → Ir a GSC Export PCU»). El link de autorización muere a los 30 min:
  lanzarlo solo cuando el usuario dice «ya».
- Cuenta GA4 «Peterson Solutions» (accounts/48728743): una propiedad por país (CU Argentina = properties/512118948, etc.).

Reglas de Felipe: trimestre = calendario completo; Q1 y Q2 2026 ya hechos, no se rehacen. Top 5 keywords (por clics) y
top 5 páginas (por vistas). North America además separado en EE. UU./Canadá (`--paises`; ~la mitad del tráfico es de otros países).

**Conversions (definición vigente, 9 oct 2026) = formularios + emails**, filtros en `scripts/ga4_export.py`:
- Formularios = vistas a páginas de gracias (thank/gracias/obrigad/agradec) **solo con pageReferrer del mismo sitio**, sin
  admin, otras gracias, empleo, academy ni reclamos (`gracias_real(host)`). Gravity y HubSpot redirigen a gracias.
- Emails = click_email fuera de empleo/academy/reclamos (`EMAIL_REAL`). **form_submit ya no se usa** (buscador + login exp-admin).
- Q3 2026: CU 600 (Arg 32, Bra 185, Chi 48, Esp 37, Méx 86, NA 62, Per 107, Por 43), PS 9 (SA 6, Iberia 3); NA: EE. UU. 47, Canadá 6.
  Antes (click_email+form_submit crudo) daba CU 1.345 / PS 51. Felipe no tiene acceso a GTM.
- Límites a declarar: cuenta vistas (no envíos únicos); sin referrer no cuenta (tiende a quedarse corto); «todas las vistas»
  a gracias es el techo (CU 475, PS 31); el total exacto de HubSpot se confirma en HubSpot.

Archivos: `scripts/reporte_trimestral.py AAAA-QN [--paises]` → `informe/trimestral/<Q>/<cu|ps>/reporte_*.json/.md`
(el .md se pasa a otra conversación para armar el reporte). `reporte_trimestral.py` importa de `ga4_export` dentro de
`website()` porque `ga4_export` importa PROPIEDADES de él (circular).

Pendientes (13 oct 2026):
1. Tablero: la pestaña «Sitios · GA4» (`ga4_export.sitio_mes()`) sigue con `FORM_REAL` → no coincide; listo cuando jul+ago+sep = CU 600 / PS 9.
2. Confirmar si gform_15 de la portada de PS Iberia es newsletter o envíos de prueba.
3. Decisión abierta: filtrar por referrer (hoy) o contar todas las vistas a gracias (cambio de una línea).
4. Academy afuera (decisión tomada, revisable).
Ver [[mapa-del-proyecto]], [[marcomms-seo-sem-dashboard]] y [[felipe-perfil]].
