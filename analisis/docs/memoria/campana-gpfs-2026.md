---
name: campana-gpfs-2026
description: "Campaña Search de Control Union USA para The Global Produce & Floral Show 2026 (Orlando, stand #851): versión final, decisiones y seguimiento pendiente"
metadata:
  node_type: memory
  type: project
  originSessionId: 3f17a333-cb57-48e9-99be-02fbe458983e
  modified: 2026-10-02T20:28:44.136Z
---

Felipe armó una campaña Search nueva (inversión nueva, USD 450 / ARS 45.600 por día) para Control Union North America
en The Global Produce & Floral Show 2026, Orlando, 14–16 oct 2026; **la expo abre solo 15 y 16 (10–17 h)**; stand
#851; landing northamerica.controlunion.com/fresh-produce-certification-expertise/ (formulario HubSpot en iframe, sin
página de gracias). En paralelo hay branding en Meta.

Versión 3 (6 oct 2026, correcciones de Felipe): una campaña «CU United States - IFPA event - Search» (7 oct; CSV en UTF-16 con tabulaciones para Editor en español, solo la campaña en pausa), ARS 10.000/día,
Maximizar clics sin CPC máx., sin fecha de fin, EE.UU.+México+Canadá sin ajustes, solo inglés, sin plantilla de seguimiento
(UTM), sin grupo de marca, sin tocar campañas existentes (las maneja el equipo). Copy: siempre «Control Union» sin país,
foco en la necesidad de quien va al show e invitar a la landing (no a agendar). Todo a la landing, incluidos 7 sitelinks
por programa; sin lead form, llamada ni imágenes. Fuente: `scripts/gpfs_2026_campana.py` → `campanas/gpfs-2026/final/todo-junto.csv`;
guía: `scripts/generar_gpfs_2026_guia.py`.
7 oct: grupo GPFS_CHECK al Typeform «Certification Check» (check informativo, no autodiagnóstico: CU no puede evaluar
preparación; eso es de Peterson). Prompt en `campanas/gpfs-2026/typeform_prompt.txt`. El grupo y su sitelink entran al CSV
con `TYPEFORM_URL` = https://form.typeform.com/to/VisEEU2n (cargado el 7 oct).

**Why:** Felipe eligió el nombre «CU United States - …» aunque el estándar de la skill es CU_US_SEARCH_…; los scripts
reconocen los dos formatos. Prefiere guías de armado paso a paso (campaña → grupo → anuncio, con el porqué) antes que
informes de pain point / mejora, y define él la estrategia (Maximizar clics, sin UTM, sin fecha de fin): no reabrirla.

**How to apply:** el objetivo es tráfico a la landing, no reuniones: después del show medir clics, visitas a la landing y
búsquedas de «control union» en EE.UU. (GSC oct vs sep). La cuenta estaba frenada por límite de gasto desde el 4 oct:
confirmar saldo antes de lanzar. Ver [[marcomms-seo-sem-dashboard]].

Editor en Windows en español: importar UTF-16 con tabulaciones (con comas lee cada fila como una campaña) y declarar la columna «Ad type» = «Responsive search ad» (sin ella marca los RSA como «tipo de fila ambiguo»). build_editor_csv.py de la skill no hace ninguna de las dos: lo resuelve `para_editor()` en gpfs_2026_campana.py.
