-- ════════════════════════════════════════════════════════════════════
-- 0001_esquema.sql — Marcomms SEO-SEM · esquema inicial
-- Idempotente: se puede correr más de una vez.
--
-- Tablas:
--   campanas       catálogo de campañas de Google Ads (sincronizado por API)
--   grupos         grupos de anuncios por campaña
--   recomendaciones tarjetas del tablero (SEM y SEO), con estado y trazabilidad
--   recomendacion_eventos  historial de cambios de estado (quién, cuándo, de qué a qué)
--   extracciones   cada corrida de extracción (Search Console / Ads)
--   metricas_mes   gasto, clics y conversiones por campaña y mes
--
-- Seguridad: RLS en todas las tablas, solo para usuarios autenticados.
-- Solo entran cuentas de los dominios del grupo (trigger sobre auth.users).
-- ════════════════════════════════════════════════════════════════════

create extension if not exists pgcrypto;

-- ─── updated_at automático ───────────────────────────────────────────
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end $$;

-- ─── Solo dominios del grupo pueden crear usuario ─────────────────────
create or replace function public.solo_dominios_del_grupo()
returns trigger language plpgsql security definer as $$
begin
  if new.email is null
     or lower(split_part(new.email, '@', 2)) not in ('onepeterson.com', 'controlunion.com') then
    raise exception 'Solo cuentas @onepeterson.com o @controlunion.com pueden acceder';
  end if;
  return new;
end $$;

drop trigger if exists solo_dominios_del_grupo on auth.users;
create trigger solo_dominios_del_grupo
  before insert on auth.users
  for each row execute function public.solo_dominios_del_grupo();

-- ─── campanas ────────────────────────────────────────────────────────
create table if not exists public.campanas (
  id            uuid primary key default gen_random_uuid(),
  ads_id        text unique,                          -- id de campaña en Google Ads
  nombre        text not null unique,                 -- nombre exacto en la cuenta
  marca         text not null check (marca in ('CU', 'PS', 'PCU')),
  unidad        text not null,                        -- España, Portugal, Canadá, Estados Unidos, Argentina…
  estado        text not null default 'ENABLED',      -- ENABLED, PAUSED, REMOVED
  presupuesto_dia numeric,                            -- ARS por día
  creada_en_cuenta boolean default false,             -- true si apareció después de la auditoría base
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
drop trigger if exists set_updated_at on public.campanas;
create trigger set_updated_at before update on public.campanas for each row execute function public.set_updated_at();
create index if not exists campanas_marca_idx on public.campanas (marca);

-- ─── grupos ──────────────────────────────────────────────────────────
create table if not exists public.grupos (
  id          uuid primary key default gen_random_uuid(),
  campana_id  uuid not null references public.campanas (id) on delete cascade,
  ads_id      text,
  nombre      text not null,
  estado      text not null default 'ENABLED',
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  unique (campana_id, nombre)
);
drop trigger if exists set_updated_at on public.grupos;
create trigger set_updated_at before update on public.grupos for each row execute function public.set_updated_at();
create index if not exists grupos_campana_idx on public.grupos (campana_id);

-- ─── recomendaciones ─────────────────────────────────────────────────
create table if not exists public.recomendaciones (
  id             uuid primary key default gen_random_uuid(),
  clave          text not null unique,               -- id estable (marca:tipo:campaña:grupo:slug) para no duplicar entre meses
  marca          text not null check (marca in ('CU', 'PS', 'PCU')),
  tipo           text not null check (tipo in ('SEM', 'SEO')),
  campana_id     uuid references public.campanas (id) on delete set null,
  grupo_id       uuid references public.grupos (id) on delete set null,
  sitio          text,                                -- SEO: propiedad de Search Console
  pagina         text,                                -- SEO: ruta de la página
  titulo         text not null,
  detalle        text not null,                       -- qué hacer, en una o dos frases
  evidencia      jsonb not null default '{}'::jsonb,  -- números que la justifican
  prioridad      text not null default 'media' check (prioridad in ('alta', 'media', 'baja')),
  estado         text not null default 'propuesta' check (estado in ('propuesta', 'en_proceso', 'hecha', 'descartada')),
  mes_alta       text not null,                       -- 'AAAA-MM' del informe que la propuso
  mes_cierre     text,                                -- 'AAAA-MM' en que pasó a hecha o descartada
  motivo_descarte text,
  verificada_api boolean not null default false,      -- true cuando la API confirma que está aplicada
  verificada_en  timestamptz,
  origen         text,                                -- informe o script que la generó
  orden          integer not null default 0,          -- posición dentro de la columna
  actualizada_por text,                               -- email de quien movió la tarjeta
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);
drop trigger if exists set_updated_at on public.recomendaciones;
create trigger set_updated_at before update on public.recomendaciones for each row execute function public.set_updated_at();
create index if not exists recomendaciones_marca_tipo_idx on public.recomendaciones (marca, tipo);
create index if not exists recomendaciones_estado_idx on public.recomendaciones (estado);
create index if not exists recomendaciones_campana_idx on public.recomendaciones (campana_id);
create index if not exists recomendaciones_mes_idx on public.recomendaciones (mes_alta);

-- ─── historial de cambios de estado ──────────────────────────────────
create table if not exists public.recomendacion_eventos (
  id                uuid primary key default gen_random_uuid(),
  recomendacion_id  uuid not null references public.recomendaciones (id) on delete cascade,
  de_estado         text,
  a_estado          text not null,
  motivo            text,
  usuario           text,
  created_at        timestamptz not null default now()
);
create index if not exists recomendacion_eventos_rec_idx on public.recomendacion_eventos (recomendacion_id);

-- ─── extracciones ────────────────────────────────────────────────────
create table if not exists public.extracciones (
  id          uuid primary key default gen_random_uuid(),
  fuente      text not null check (fuente in ('search_console', 'google_ads')),
  corrida_en  timestamptz not null default now(),
  desde       date,
  hasta       date,
  filas       integer,
  detalle     jsonb not null default '{}'::jsonb,     -- cortes y filas por corte
  created_at  timestamptz not null default now()
);
create index if not exists extracciones_fuente_idx on public.extracciones (fuente, corrida_en desc);

-- ─── metricas_mes ────────────────────────────────────────────────────
create table if not exists public.metricas_mes (
  id            uuid primary key default gen_random_uuid(),
  campana_id    uuid not null references public.campanas (id) on delete cascade,
  mes           text not null,                        -- 'AAAA-MM'
  coste         numeric not null default 0,
  clics         integer not null default 0,
  impresiones   integer not null default 0,
  conversiones  numeric not null default 0,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  unique (campana_id, mes)
);
drop trigger if exists set_updated_at on public.metricas_mes;
create trigger set_updated_at before update on public.metricas_mes for each row execute function public.set_updated_at();

-- ─── RLS: solo autenticados ───────────────────────────────────────────
do $$
declare t text;
begin
  foreach t in array array['campanas', 'grupos', 'recomendaciones', 'recomendacion_eventos', 'extracciones', 'metricas_mes'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('drop policy if exists "auth users full access" on public.%I', t);
    execute format('create policy "auth users full access" on public.%I for all to authenticated using (true) with check (true)', t);
  end loop;
end $$;

-- ─── Realtime ────────────────────────────────────────────────────────
do $$
declare t text;
begin
  foreach t in array array['recomendaciones', 'extracciones'] loop
    if not exists (
      select 1 from pg_publication_tables where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = t
    ) then
      execute format('alter publication supabase_realtime add table public.%I', t);
    end if;
  end loop;
end $$;
