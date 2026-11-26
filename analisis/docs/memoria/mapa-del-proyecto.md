---
name: mapa-del-proyecto
description: "Dónde está cada cosa (carpetas, scripts, datos, web, accesos) para arrancar una sesión nueva sin releer todo"
metadata:
  node_type: memory
  type: reference
  originSessionId: 3f17a333-cb57-48e9-99be-02fbe458983e
  modified: 2026-10-08T15:42:07.224Z
---

- **Análisis Ads × Search Console**: `Documentos/Optimizaciónes SEO-SEM/proyecto/` — brief en `proyecto/CLAUDE.md` (leerlo
  primero). Scripts en `proyecto/scripts/`, datos en `proyecto/datos/`, informes PDF en `proyecto/informe/`.
  - Extracción Ads (solo lectura): `ads_export.py`, `ads_estructura.py`, `ads_diario.py` (gasto por día). Search Console:
    `gsc_historico.py`. Recomendaciones para la web: `exportar_recomendaciones.py`.
  - Accesos: Google Ads con tmpcugroup@gmail.com, Search Console con tmisrahi@onepeterson.com
    (`ads_auth.py --ads|--gsc CUENTA`; app «En producción», no vence).
- **Web Marcomms SEO-SEM**: repo `Documentos/Marcomms SEO-SEM/` (GitHub AnnaPCU/Marcomms-Seo-Sem), en producción en
  https://marcomms-seo-sem.vercel.app. Datos en Supabase, esquema `seo_sem` del proyecto cogdfbonpvvuzhurmvlq, se cargan
  con `scripts/publicar.py --sql` + MCP execute_sql. Ver [[marcomms-seo-sem-dashboard]].
- **Campañas nuevas**: `proyecto/campanas/<nombre>/` (p. ej. gpfs-2026: fuente `scripts/gpfs_2026_campana.py`). Ver [[campana-gpfs-2026]].
- **Skills útiles**: paid-media-pcu (campañas y CSV de Editor), manual-de-marca-pcu (tono y marca).
