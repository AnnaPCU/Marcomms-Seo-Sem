# Marcomms SEO-SEM — guía para trabajar en este repo

Tablero interno de MarComms (la agencia interna del grupo Peterson Control Union) para seguir las
recomendaciones SEM y SEO que salen del proyecto de análisis `../Optimizaciónes SEO-SEM/proyecto`.
Leé también `PROJECT_CONTEXT.md` (qué es y por qué) y `DEPLOY.md` (cómo se publica).

## Identidad y marca

- La web representa a **MarComms**: azul marino `#1b1e42` y azul `#009ceb`, logos en `public/marca/`.
- Control Union y Peterson Solutions son **clientes** del tablero. Sus contenidos se muestran con chips de
  texto en la paleta MarComms. **Nunca** se usan sus colores de marca (Cyan `#3eb2ed`, Aqua `#44cbce`,
  Yellow `#f1e747`) ni sus logos, y nunca se mezclan sus datos en una misma tarjeta.
- Vocabulario: Control Union certifica y audita; Peterson acompaña y prepara para certificar. Las
  recomendaciones que se cargan ya respetan eso; si escribís texto nuevo, mantenelo.

## Stack

Vite 8 · React 19 · TypeScript · Tailwind 3 · Supabase (Postgres + Auth + Realtime) · react-router 7 ·
@dnd-kit · lucide-react · Vitest · Vercel.

## Estructura

```
src/lib/          supabase.ts (único cliente) · database.types.ts (tipos de la base)
src/constants/    estados, marcas, tipos, prioridades, dominios permitidos
src/services/     acceso a datos: una función por operación, fromRow/toRow, sin React
src/hooks/        useAuth (sesión) · useDatos (un hook por recurso, realtime en recomendaciones)
src/components/   shared (Layout, Ui) · tablero (Tablero, TarjetaRec, DetalleRec, Filtros, MotivoDescarte)
src/routes/       Login · Inicio · Sem · Seo · Historial
src/utils/        formato.ts (+ tests)
supabase/         migrations/0001_esquema.sql (idempotente)
scripts/          publicar.py (carga desde el proyecto de análisis)
docs/             DECISIONES.md
```

## Reglas

1. **Nada fuera de `src/services` importa `supabase.ts`.** Los componentes usan hooks; los hooks usan servicios.
2. Componentes de menos de 500 líneas; si crece, se parte.
3. Migraciones numeradas e idempotentes en `supabase/migrations/`. Después de cambiar el esquema, regenerar
   `src/lib/database.types.ts` (`supabase gen types typescript --project-id <ref>`).
4. Ninguna clave secreta en el repo ni en Vercel: solo `VITE_SUPABASE_URL` y `VITE_SUPABASE_PUBLISHABLE_KEY`.
   El service role key vive en el entorno local de quien corre `scripts/publicar.py`.
5. Antes de pushear: `npm run verificar` (typecheck + tests + build) tiene que pasar.
6. Una sola rama `main`; cada push despliega a producción en Vercel.
7. Español rioplatense en la interfaz y en los comentarios. Sin emojis.

## Cómo se renueva cada mes

1. En el proyecto de análisis: extracción GSC y Ads, `analisis*.py`, informes.
2. `python scripts/exportar_recomendaciones.py AAAA-MM` allá → `informe/recomendaciones.json`.
3. Acá: `python scripts/publicar.py` con `SUPABASE_URL` y `SUPABASE_SERVICE_KEY` en el entorno.
   Las tarjetas nuevas entran como «propuesta»; las que ya existían conservan su estado.
