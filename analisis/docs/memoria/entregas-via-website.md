---
name: entregas-via-website
description: Felipe no quiere más el informe de gasto de Ads por chat; todo se consulta en la web Marcomms SEO-SEM
metadata:
  node_type: memory
  type: feedback
  originSessionId: 3f17a333-cb57-48e9-99be-02fbe458983e
  modified: 2026-09-30T13:30:58.736Z
---

No enviar más el HTML «Gasto Google Ads por cliente» (ni versiones nuevas) por el chat. Desde el 30 sep 2026 todo se
consulta directo en https://marcomms-seo-sem.vercel.app (Inicio = presupuesto y gasto).

**Why:** Felipe lo pidió explícitamente: «a partir de ahora la idea es acceder directamente todo desde la website».
**How to apply:** después de una extracción, cargar los datos en Supabase (scripts/publicar.py --sql) y avisar que la
web está actualizada; el HTML estático se puede seguir generando localmente pero no se manda. Ver [[marcomms-seo-sem-dashboard]].
Referencia visual para la web: MarComms Reports (barra superior blanca, pestañas con ícono, títulos de sección azules
en mayúsculas con línea, KPIs con borde de color, franjas azul noche).
