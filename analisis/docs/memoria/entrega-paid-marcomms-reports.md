---
name: entrega-paid-marcomms-reports
description: Entrega mensual de Paid Media (Google Ads + Meta) de SEO-SEM al repo MarComms-Reports: script, clon sparse, tarea del día 2 y trampas
metadata:
  type: project
---

Desde el 17 nov 2026, SEO-SEM le entrega a MarComms-Reports (AnnaPCU/MarComms-Reports) las métricas de Paid Media del
mes cerrado según su `docs/ENTREGA_PAID_DESDE_SEO_SEM.md`. Allá una tarea las procesa y publica del 3 al 10.
- Script: `proyecto/scripts/entrega_paid.py` (sin args = mes anterior; `--push` sube; `--forzar`, `--sin-meta`, `--sin-google`).
  Google: 3 CSV Search del mes en moneda de la cuenta (ARS) con 2 líneas de título+rango arriba (build_detail.py de
  allá saltea 2 líneas aunque el contrato diga «encabezado en la primera fila»). Meta: vuelos agrupados por
  marca + evento (2º segmento del nombre), terminados en el mes (último día con gasto, ninguno ACTIVE), y salta los que
  ya figuran en el repo (`git grep` en origin/main).
- Clon sparse en `Optimizaciónes SEO-SEM/_repos/paid-entrega` (metricas/paid-media, scripts/paid, docs) con
  core.protectNTFS=false y core.longpaths: el repo tiene archivos con «:» que Windows no acepta.
- Tarea `entrega-paid-media-marcomms-reports`, día 3 a las 7:00 (Felipe la pasó del 2 al 3; corre cuando abre la app).
- Oct 2026 entregado el 17 nov (commit 6551d9a en main: 43 campañas, ARS 4.040.805,59, cuadra con metricas_mes).
- Peterson ARG - Aapresid (ago 2026, Meta, USD) no figura en el repo como entregado.
Ver [[integracion-meta-ads]], [[marcomms-seo-sem-dashboard]], [[pilares-paid-media-hub]].
