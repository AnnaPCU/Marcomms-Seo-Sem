---
name: nombre-cuc-usa
description: "Pedido del cliente (10 nov 2026): todo lo de Control Union en Estados Unidos se llama «CUC USA» (mayúsculas, con espacio)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 3f17a333-cb57-48e9-99be-02fbe458983e
  modified: 2026-11-10T21:04:06.091Z
---

Desde el 10 nov 2026, por pedido del cliente, todo el contenido de Control Union en Estados Unidos se llama **«CUC USA»** (todo en mayúsculas, «CUC», espacio, «USA»). Se comunica así en tarjetas, informes, anuncios y en el tablero.

**Why:** lo pidió el cliente y así se comunica hacia afuera.
**How to apply:** en el tablero la unidad/país es «CUC USA» (antes «Estados Unidos»: actualizado en seo_sem.campanas, evidencia.unidad, publicar.py, analisis_gasto.py, generar_vista_gasto.py, exportar_recomendaciones.py, ga4.ts). `marca_de` reconoce el prefijo «CUC » / «CUC_» como CU, por si renombran las campañas en Google Ads. Los nombres reales de campaña («CU United States - …») se citan tal cual mientras sigan así en la cuenta. Canadá sigue aparte. La app del Hub (`ads_pilares_paid_media.py`) todavía usa «Estados Unidos»: no se tocó.
