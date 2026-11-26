---
name: prueba-google-cloud
description: El proyecto de Google Cloud de las APIs (GSC, GA4, Ads) está en prueba gratuita que vence ~15 dic 2026; qué depende de él y qué hacer
metadata:
  type: project
---

`proyecto/client_secret.json` es del proyecto `project-3ec2e270-0dba-489f-8f0` (cuenta de prueba gratuita de Google Cloud
de Tomas Misrahi). Search Console, GA4 y Google Ads (`google-ads.yaml`) usan **el mismo cliente OAuth** de ese proyecto.
El 15 nov 2026 llegó el aviso «te quedan 30 días» → la prueba vence ~15 dic 2026; luego 30 días de gracia (~14 ene 2027).

Las tres APIs son gratuitas (no facturan); la doc de Google no dice explícitamente si siguen andando con la facturación
desactivada. La web (Vercel + Supabase) no depende de este proyecto; sí las extracciones (cierre de mes, impacto, trimestrales).
Recomendado (16 nov): probar ya desvinculando la facturación del proyecto y correr las 3 extracciones; si falla, volver a
vincular o pasar a cuenta pagada. Plan B: proyecto nuevo con cuenta de la empresa, nuevo client_secret y re-autorizar los
3 tokens (el developer token de Ads es del MCC, no cambia; el trámite de acceso básico se re-hace en el proyecto nuevo).
Ver [[acceso-basico-google-ads]], [[reportes-trimestrales-gsc-ga4]], [[mapa-del-proyecto]].
