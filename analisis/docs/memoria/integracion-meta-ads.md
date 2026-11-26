---
name: integracion-meta-ads
description: "Integración con Meta Ads (31 oct 2026): extractor meta_export.py, subida meta_subir.py, MCP oficial de Meta; bloqueado esperando app + token del portfolio"
metadata:
  node_type: memory
  type: project
  originSessionId: 3f17a333-cb57-48e9-99be-02fbe458983e
  modified: 2026-11-10T20:49:04.187Z
---

Pedido del usuario (30 oct 2026): leer de Meta Ads todo lo que se pueda (incluida la puja, que en Google no se trajo) y poder **subir campañas desde acá**.

Hecho el 31 oct 2026 en `proyecto/`:
- `scripts/meta_api.py` (cliente Graph API v26.0, paginado, cupos), `scripts/meta_export.py` (cuentas, campañas con bid_strategy/presupuesto, conjuntos con segmentación/optimización/puja, anuncios con creativo y rechazo, audiencias, píxeles, historial de cambios, insights por anuncio y día con acciones, desgloses edad/sexo, plataforma, país, dispositivo; salida separada por marca en `datos/meta/api/<marca>/`, lo de cuenta en «cuenta»).
- `scripts/meta_subir.py`: JSON → campaña/conjuntos/anuncios **siempre PAUSED**, modo local / `--validar` (validate_only) / `--subir`; valida prefijo, dominio y vocabulario por marca (usa `PROHIBIDO` de aplicar_revision).
- `META_ADS.md`: pasos para el admin del portfolio. Probado solo con API simulada: falta token real.
- Escritura conversacional: MCP oficial `https://mcp.facebook.com/ads` (`claude mcp add --transport http --client-id <APP_ID> meta-ads https://mcp.facebook.com/ads`), crea en pausa, `ads_activate_entity` activa; token de sistema debe ser rol Empleado.

**Conectado (10 nov 2026):** portfolio «Marcomms - Cuentas de META» (Tomas tiene control total); app de desarrollador creada con otra cuenta de Facebook y conectada al portfolio por «Connect an app ID» (la cuenta de onepeterson no puede registrarse como desarrollador). Usuario del sistema «marcomms-tablero» (Empleado), token sin vencimiento en `proyecto/meta-ads.json` con `cuentas`: act_1045510044627021 → CU (ARS), act_1691926654833918 → PS (**USD**). La marca sale de la cuenta, no del nombre (las de Peterson se llaman «Peterson …»). Primera extracción 2026 verificada: suma por campaña = amount_spent de cada cuenta (ARS 451.939,53 / USD 200,84). Todas las campañas en PAUSA; las de objetivo leads no miden leads (CU: conversaciones de WhatsApp). El token se pegó en el chat el 10 nov: pendiente regenerarlo y pegarlo directo en el archivo.

**Decisión 10 nov 2026:** Meta NO va al tablero de optimizaciones por ahora (son campañas one-shot de eventos). MCP oficial configurado en `Optimizaciónes SEO-SEM/.mcp.json` («meta-ads») con headersHelper `proyecto/scripts/meta_mcp_headers.py` (Bearer del token de sistema; probado por HTTP: 99 herramientas). App ID 3772720962878154. OAuth de Claude Code descartado por bugs conocidos de redirect.

**Why:** extender el tablero a Meta como Google y operar campañas sin salir de Claude.
**How to apply:** pendiente del usuario: qué cuentas/marcas, app de Meta y token en `meta-ads.json`. Después: `--probar`, primera extracción, migración `plataforma` en seo_sem y vista Meta en el tablero. Cualquier creación/edición/activación en Meta requiere «sí» explícito por acción. Ver [[marcomms-seo-sem-dashboard]], [[reglas-tarjetas-sem]].
