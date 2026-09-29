# Despliegue

## Piezas

| Pieza | Dónde | Nombre |
|---|---|---|
| Código | GitHub | `AnnaPCU/marcomms-seo-sem` (privado), rama `main` |
| Base y auth | Supabase | esquema `seo_sem` dentro de «MarComms Hub Project» (`cogdfbonpvvuzhurmvlq`, org marcomms-hub) |
| Hosting | Vercel | proyecto `marcomms-seo-sem`, equipo `anna-6241s-projects` |

Cada push a `main` construye y publica en Vercel. No hay entorno de staging: se verifica local antes de pushear.

## Primera vez

1. **Supabase**: la migración `supabase/migrations/0001_esquema.sql` ya está aplicada en el proyecto del Hub
   (crea el esquema `seo_sem`, lo expone por REST y deja RLS restringido a los dominios del grupo). Para el
   login: en Authentication → Providers habilitar Google (Client ID y Secret de un cliente OAuth web en Google
   Cloud, con `https://cogdfbonpvvuzhurmvlq.supabase.co/auth/v1/callback` como URI de redirección). En
   Authentication → URL configuration agregar la URL de Vercel a Redirect URLs. El enlace por correo funciona
   sin configurar nada, con el límite de envíos del SMTP de Supabase.
2. **Vercel**: importar el repo. Framework Vite, build `npm run build`, salida `dist`. Variables:
   `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, `VITE_APP_NAME`.
3. **Datos**: `python scripts/publicar.py --sql supabase/seed/carga_AAAA-MM.sql` genera un SQL idempotente
   que se corre en el SQL editor del proyecto (o por el conector). No necesita claves. El modo REST con
   `SUPABASE_SERVICE_KEY` queda como alternativa.

## Local

```bash
cp .env.example .env.local   # completar con la URL y la publishable key
npm install
npm run dev                  # http://localhost:5174
npm run verificar            # typecheck + tests + build, antes de cada push
```

## Cambios de esquema

Nueva migración numerada en `supabase/migrations/`, siempre dentro de `seo_sem` (nunca tocar `public`, que es del
Hub), aplicarla, regenerar tipos con `--schema seo_sem`, commit de ambas cosas.
