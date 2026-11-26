---
name: pilares-paid-media-hub
description: "Histórico de Google Ads exportado para cargar en MarComms Hub → Pilares → Paid Media (public.campaigns type 'paid'): archivos, mapeo y decisiones decisiones al 22 oct 2026"
metadata:
  node_type: memory
  type: project
  originSessionId: d43d3ed6-e625-480e-ab88-664287afb2fd
  modified: 2026-10-22T17:59:06.716Z
---

22 oct 2026: `proyecto/scripts/ads_pilares_paid_media.py` saca todas las campañas (cualquier tipo y estado) de las dos
cuentas de Ads y escribe en `proyecto/informe/pilares_paid_media/` un JSON + Excel por marca (cu 31, ps 8, pcu 4) más `INSTRUCCIONES_CLAUDE_CODE.md` para el Claude Code del repo `Documentos/MarComms Hub`. Una fila por
campaña; las migradas de la cuenta vieja a la nueva se juntan por nombre. USD con promedio mensual BCRA. Verificado
contra la API: ARS 6.763.407 y EUR 11.725, 97 campañas (3 nunca publicadas quedan afuera).

Mapeo de la app (src/services/campaignsService.js, constants/campaigns.js): pasos paid = brief, creativities, launch;
data.{platforms, paidMode always_on|one_shot, duration, objective posicionamiento|conversion, detail}; platform_investment =
«Inversión oficina (USD)»; budget = Fee MarComms. El histórico va en data.google_ads con clave_externa para no duplicar.

**Decidido 22 oct 2026:** las 4 «PCU» ISO 27001 (Argentina y España) se cargan con unidad «PCU» y las paga Control Union
España (`data.facturar_a`; la app local no tiene campo de pagador ni «PCU» en markets.js: el instructivo pide agregarlos).
**Decidido 22 oct 2026:** las 23 sin prefijo de marca (Growr y Peterson Technologies 2024–2026, ~10.200 USD) NO se cargan; el script ya no las exporta.
Ver [[marcomms-seo-sem-dashboard]], [[mapa-del-proyecto]].
