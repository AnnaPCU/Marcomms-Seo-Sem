---
name: reglas-tarjetas-sem
description: "Cómo quiere Felipe las tarjetas de «SEM · campañas»: una acción una tarjeta, siempre campaña/grupo/anuncio, keywords y negativas en grupos nuevos, motivo y prioridad por propuesta"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 3f17a333-cb57-48e9-99be-02fbe458983e
  modified: 2026-11-10T21:25:11.863Z
---

Felipe (21 oct 2026) corrigió las tarjetas SEM del tablero:
1. Una acción, una tarjeta: no repartir una recomendación en varias (el caso fue ISCC CU Argentina: «grupo nuevo» y «anuncio» separados). Lo normal es una tarjeta abierta por campaña con pasos.
2. Siempre el nombre completo de la campaña y, si aplica, el grupo y el id del anuncio.
3. Grupo nuevo → keywords recomendadas (concordancia y motivo) y decisión explícita sobre negativas.
4. Ajuste de anuncio → motivo del cambio y motivo de cada título/descripción; destacar (`prioritario`) las que de verdad conviene hacer.
5. (28 oct 2026, también para SEO) Cada paso dice exactamente qué cargar: lista `items` con el texto literal (keyword/negativa con concordancia, título, title/meta/H1, URL de 301), destino y motivo. Nunca «cargar las negativas de la tabla» o «sumar tres exactas» sin nombrarlas (pasó en ISCC CU Argentina). Un cambio de concordancia son dos ítems: agregar la nueva y pausar la vieja.

6. (10 nov 2026) **Al grano**: el detalle muestra dónde, el problema (`detalle`, 2–3 frases), la solución (`evidencia.resumen`, una línea) y qué hacer en orden (pasos con items, separados por campaña/anuncio). `por_que`/`ya_hecho` quedan plegados; las tablas de keywords/negativas/anuncios no se muestran (siguen en la evidencia para el Excel). Commit efdf08d.
7. (10 nov 2026) «Hecha» = aplicó la mayor parte, no todo; «descartada» = la mayor parte no tenía sentido. Al verificar o medir impacto, mirar qué ítems se aplicaron.

**Why:** las tarjetas viejas no le decían dónde ni por qué, y no podía distinguir lo importante de las variantes; el 28 oct no supo qué negativas ni qué exactas cargar.
**How to apply:** usar la ficha «campana» (ver [[marcomms-seo-sem-dashboard]]); validar con `aplicar_revision.validar_campana` (también comprueba que lo que se quita exista hoy en el anuncio y el tope 15 títulos / 4 descripciones). Antes de citar una cifra, calcularla desde los CSV; al releer el SQL antes de cargar aparecieron errores reales (un texto a quitar que no existía, un CPC mal atribuido). Ver [[felipe-perfil]].
