# Despliegue

## Piezas

| Pieza | Dónde | Nombre |
|---|---|---|
| Código | GitHub | `AnnaPCU/marcomms-seo-sem` (privado), rama `main` |
| Base y auth | Supabase | proyecto «Marcomms SEO-SEM», región `sa-east-1` |
| Hosting | Vercel | proyecto `marcomms-seo-sem`, equipo `anna-6241s-projects` |

Cada push a `main` construye y publica en Vercel. No hay entorno de staging: se verifica local antes de pushear.

## Primera vez

1. **Supabase**: crear el proyecto, correr `supabase/migrations/0001_esquema.sql` en el SQL editor (o por MCP),
   y en Authentication → Providers habilitar Google (Client ID y Secret de un cliente OAuth web en Google
   Cloud, con `https://<ref>.supabase.co/auth/v1/callback` como URI de redirección). En Authentication → URL
   configuration poner la URL de Vercel como Site URL y agregarla a Redirect URLs.
2. **Vercel**: importar el repo. Framework Vite, build `npm run build`, salida `dist`. Variables:
   `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, `VITE_APP_NAME`.
3. **Datos**: en la máquina de quien corre el análisis, con `SUPABASE_URL` y `SUPABASE_SERVICE_KEY` en el
   entorno, `python scripts/publicar.py`.

## Local

```bash
cp .env.example .env.local   # completar con la URL y la publishable key
npm install
npm run dev                  # http://localhost:5174
npm run verificar            # typecheck + tests + build, antes de cada push
```

## Cambios de esquema

Nueva migración numerada en `supabase/migrations/`, aplicarla, regenerar tipos, commit de ambas cosas.
