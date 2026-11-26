---
name: acceso-basico-google-ads
description: "Trámite para pasar la Google Ads API de \"explorer\" a \"básico\" (Planificador de palabras clave): qué está hecho y qué falta, al 20 oct 2026"
metadata:
  node_type: memory
  type: project
  originSessionId: e6116b5b-6b36-4c88-8cde-378ca88048c2
  modified: 2026-10-20T20:32:10.870Z
---

La Google Ads API está en nivel "explorer": bloquea KeywordPlanIdeaService (Planificador), AudienceInsights y ReachPlan.
`proyecto/scripts/ads_planner.py` ya está escrito y falla con "not allowed for use with explorer access". Pujas, CPC
real y términos de búsqueda sí se leen. El trámite ahora es en Google Cloud (no en el Centro de API de Ads).

Hecho (19–20 oct 2026):
- Página pública https://marcomms-seo-sem.vercel.app/privacidad (`public/privacidad.html` + rewrite en `vercel.json`),
  portada estática en `index.html` con enlace, enlace en Login. Contacto publicado: tmisrahi@onepeterson.com.
- Search Console: propiedad de prefijo de URL `https://marcomms-seo-sem.vercel.app/` verificada (meta tag en
  `index.html` + archivo `public/google306ead38070a45f1.html`; no borrarlos o se pierde la verificación).
- Branding en Google Cloud (proyecto `project-3ec2e270-0dba-489f-8f0`): dominio autorizado `marcomms-seo-sem.vercel.app`,
  sin logo. El primer "Verify Branding" falló porque el sitio aún no estaba verificado.

Falta: desde el 21 oct 2026, reintentar la verificación de marca («Corregí los problemas»), "Publish branding", y en
console.cloud.google.com/google/ads-apis/overview → Upgrade access level → Apply for access (Basic). Al aprobarse,
volver a correr `ads_planner.py historico` para confirmar. El token no cambia.

**Why:** el usuario quiere que Claude saque volúmenes, rangos de puja e ideas de keywords sin consultas manuales.
**How to apply:** si retoma el tema, arrancar por el paso pendiente. El usuario no es técnico con Google Cloud: guiarlo
clic por clic y pedir capturas. Ver [[mapa-del-proyecto]], [[marcomms-seo-sem-dashboard]].
