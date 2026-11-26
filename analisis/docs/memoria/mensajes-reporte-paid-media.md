---
name: mensajes-reporte-paid-media
description: Plantilla fija de apertura y cierre para los mensajes a clientes (CU/PS por país) que acompañan el reporte mensual de paid media
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5d249d39-aea3-4db5-aaa6-ace2968e11a4
  modified: 2026-10-19T15:09:47.828Z
---

Los mensajes que acompañan el reporte de paid media van en español (aunque el país sea Canadá o Portugal) y siempre:

**Apertura** (dos párrafos):
"Les adjunto el resumen de Paid Media de Control Union <País> correspondiente a <mes>. Recuerden descargarlo y abrirlo desde cualquier navegador para poder verlo correctamente."
"Durante el mes, junto a @Felipe Señorans mantuvimos <N> campañas de búsqueda activas en Google Ads, donde la inversión fue de unos <gasto> sobre un presupuesto de unos <presupuesto>."

**Cierre** (reemplaza al de "organizar una reunión"):
"Nos gustaría que nos comenten qué opinan de esta propuesta y, si llegan a estar interesados en cambiar algo del panorama general, podemos concretar una reunión para verlo."

Cuerpo: secciones "Qué conseguimos" y "Oportunidad" (estilo de los mensajes CU Cert ARG / PS ARG). Montos redondeados en la moneda local del cliente (la cuenta factura en ARS; convertir al tipo de cambio oficial BNA del día y avisar cuál se usó). CTR explicado con "de cada 100 personas…". Nunca afirmar "inversión bajo control" si alguna campaña pasó +5% del presupuesto.

**Why:** pedido explícito de la usuaria (oct 2026) al revisar el mensaje de CU España; Felipe figura como co-responsable de las campañas ([[felipe-perfil]]).
**How to apply:** cada vez que pida "el mensaje" de un país/marca para el envío del reporte. Ver [[mapa-del-proyecto]] para sacar los datos (Google Ads API, solo lectura).
