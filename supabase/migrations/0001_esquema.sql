-- ════════════════════════════════════════════════════════════════════
-- 0001_esquema.sql — Marcomms SEO-SEM · esquema inicial
-- Vive en el esquema `seo_sem` del proyecto de Supabase "MarComms Hub Project" (cogdfbonpvvuzhurmvlq),
-- separado del esquema `public` que usa el Hub. Idempotente: se puede correr más de una vez.
-- Aplicada el 29 sep 2026 como migración "seo_sem_0001_esquema".
--
-- Tablas:
--   campanas               catálogo de campañas de Google Ads (sincronizado por API)
--   grupos                 grupos de anuncios por campaña
--   recomendaciones        tarjetas del tablero (SEM y SEO), con estado y trazabilidad
--   recomendacion_eventos  historial de cambios de estado (quién, cuándo, de qué a qué)
--   extracciones           cada corrida de extracción (Search Console / Ads)
--   metricas_mes           gasto, clics y conversiones por campaña y mes
--
-- Seguridad: RLS en todas las tablas; solo usuarios autenticados cuyo correo sea @onepeterson.com o
-- @controlunion.com (función seo_sem.es_del_grupo sobre el JWT). No se toca auth.users ni nada del Hub.
-- ════════════════════════════════════════════════════════════════════

create extension if not exists pgcrypto;
create schema if not exists seo_sem;
grant usage on schema seo_sem to anon, authenticated, service_role;
alter default privileges in schema seo_sem grant all on tables to anon, authenticated, service_role;
alter default privileges in schema seo_sem grant all on sequences to anon, authenticated, service_role;
alter default privileges in schema seo_sem grant all on functions to anon, authenticated, service_role;

-- ─── updated_at automático ───────────────────────────────────────────
create or replace function seo_sem.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end $$;

-- ─── Solo cuentas del grupo (se evalúa sobre el token de la sesión) ───
create or replace function seo_sem.es_del_grupo()
returns boolean language sql stable as $$
  select coalesce(lower(split_part(auth.jwt() ->> 'email', '@', 2)) in ('onepeterson.com', 'controlunion.com'), false)
$$;

-- ─── campanas ────────────────────────────────────────────────────────
create table if not exists seo_sem.campanas (
  id            uuid primary key default gen_random_uuid(),
  ads_id        text unique,                          -- id de campaña en Google Ads
  nombre        text not null unique,                 -- nombre exacto en la cuenta
  marca         text not null check (marca in ('CU', 'PS', 'PCU')),
  unidad        text not null,                        -- España, Portugal, Canadá, Estados Unidos, Argentina…
  estado        text not null default 'ENABLED',
  presupuesto_dia numeric,                            -- ARS por día
  creada_en_cuenta boolean default false,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
drop trigger if exists set_updated_at on seo_sem.campanas;
create trigger set_updated_at before update on seo_sem.campanas for each row execute function seo_sem.set_updated_at();
create index if not exists campanas_marca_idx on seo_sem.campanas (marca);

-- ─── grupos ──────────────────────────────────────────────────────────
create table if not exists seo_sem.grupos (
  id          uuid primary key default gen_random_uuid(),
  campana_id  uuid not null references seo_sem.campanas (id) on delete cascade,
  ads_id      text,
  nombre      text not null,
  estado      text not null default 'ENABLED',
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  unique (campana_id, nombre)
);
drop trigger if exists set_updated_at on seo_sem.grupos;
create trigger set_updated_at before update on seo_sem.grupos for each row execute function seo_sem.set_updated_at();
create index if not exists grupos_campana_idx on seo_sem.grupos (campana_id);

-- ─── recomendaciones ─────────────────────────────────────────────────
create table if not exists seo_sem.recomendaciones (
  id             uuid primary key default gen_random_uuid(),
  clave          text not null unique,               -- id estable (marca:tipo:campaña|sitio:slug) para no duplicar entre meses
  marca          text not null check (marca in ('CU', 'PS', 'PCU')),
  tipo           text not null check (tipo in ('SEM', 'SEO')),
  campana_id     uuid references seo_sem.campanas (id) on delete set null,
  grupo_id       uuid references seo_sem.grupos (id) on delete set null,
  sitio          text,                                -- SEO: propiedad de Search Console
  pagina         text,                                -- SEO: ruta de la página
  titulo         text not null,
  detalle        text not null,
  evidencia      jsonb not null default '{}'::jsonb,
  prioridad      text not null default 'media' check (prioridad in ('alta', 'media', 'baja')),
  estado         text not null default 'propuesta' check (estado in ('propuesta', 'en_proceso', 'hecha', 'descartada')),
  mes_alta       text not null,                       -- 'AAAA-MM' del informe que la propuso
  mes_cierre     text,
  motivo_descarte text,
  verificada_api boolean not null default false,
  verificada_en  timestamptz,
  origen         text,
  orden          integer not null default 0,
  actualizada_por text,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);
drop trigger if exists set_updated_at on seo_sem.recomendaciones;
create trigger set_updated_at before update on seo_sem.recomendaciones for each row execute function seo_sem.set_updated_at();
create index if not exists recomendaciones_marca_tipo_idx on seo_sem.recomendaciones (marca, tipo);
create index if not exists recomendaciones_estado_idx on seo_sem.recomendaciones (estado);
create index if not exists recomendaciones_campana_idx on seo_sem.recomendaciones (campana_id);
create index if not exists recomendaciones_mes_idx on seo_sem.recomendaciones (mes_alta);

-- ─── historial de cambios de estado ──────────────────────────────────
create table if not exists seo_sem.recomendacion_eventos (
  id                uuid primary key default gen_random_uuid(),
  recomendacion_id  uuid not null references seo_sem.recomendaciones (id) on delete cascade,
  de_estado         text,
  a_estado          text not null,
  motivo            text,
  usuario           text,
  created_at        timestamptz not null default now()
);
create index if not exists recomendacion_eventos_rec_idx on seo_sem.recomendacion_eventos (recomendacion_id);

-- ─── extracciones ────────────────────────────────────────────────────
create table if not exists seo_sem.extracciones (
  id          uuid primary key default gen_random_uuid(),
  fuente      text not null check (fuente in ('search_console', 'google_ads')),
  corrida_en  timestamptz not null default now(),
  desde       date,
  hasta       date,
  filas       integer,
  detalle     jsonb not null default '{}'::jsonb,
  created_at  timestamptz not null default now()
);
create index if not exists extracciones_fuente_idx on seo_sem.extracciones (fuente, corrida_en desc);

-- ─── metricas_mes ────────────────────────────────────────────────────
create table if not exists seo_sem.metricas_mes (
  id            uuid primary key default gen_random_uuid(),
  campana_id    uuid not null references seo_sem.campanas (id) on delete cascade,
  mes           text not null,                        -- 'AAAA-MM'
  coste         numeric not null default 0,
  clics         integer not null default 0,
  impresiones   integer not null default 0,
  conversiones  numeric not null default 0,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  unique (campana_id, mes)
);
drop trigger if exists set_updated_at on seo_sem.metricas_mes;
create trigger set_updated_at before update on seo_sem.metricas_mes for each row execute function seo_sem.set_updated_at();

-- ─── Permisos y RLS: solo autenticados del grupo ─────────────────────
grant all on all tables in schema seo_sem to anon, authenticated, service_role;
grant all on all sequences in schema seo_sem to anon, authenticated, service_role;
do $$
declare t text;
begin
  foreach t in array array['campanas', 'grupos', 'recomendaciones', 'recomendacion_eventos', 'extracciones', 'metricas_mes'] loop
    execute format('alter table seo_sem.%I enable row level security', t);
    execute format('drop policy if exists "grupo acceso total" on seo_sem.%I', t);
    execute format('create policy "grupo acceso total" on seo_sem.%I for all to authenticated using (seo_sem.es_del_grupo()) with check (seo_sem.es_del_grupo())', t);
  end loop;
end $$;

-- ─── Realtime ────────────────────────────────────────────────────────
do $$
declare t text;
begin
  foreach t in array array['recomendaciones', 'extracciones'] loop
    if not exists (
      select 1 from pg_publication_tables where pubname = 'supabase_realtime' and schemaname = 'seo_sem' and tablename = t
    ) then
      execute format('alter publication supabase_realtime add table seo_sem.%I', t);
    end if;
  end loop;
end $$;

-- ─── Exponer el esquema por la API REST (PostgREST) ──────────────────
-- Equivale a Settings → API → Exposed schemas. Esta configuración de rol tiene prioridad sobre la del
-- dashboard: si alguien cambia la lista allá, mantener las dos iguales.
alter role authenticator set pgrst.db_schemas = 'public, graphql_public, seo_sem';
notify pgrst, 'reload config';
