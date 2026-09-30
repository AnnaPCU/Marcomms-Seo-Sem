-- ════════════════════════════════════════════════════════════════════
-- 0002_gasto_por_grupo.sql — Marcomms SEO-SEM
-- Para la vista de presupuesto en Inicio:
--   · metricas_mes guarda qué días cubre cada mes cargado (desde, hasta, dias), así el gasto por día
--     se calcula sobre los días con datos y no sobre el mes completo.
--   · metricas_grupo_mes: gasto por grupo de anuncios y mes, para abrir cada campaña en sus grupos.
-- Idempotente. Solo toca el esquema seo_sem.
-- ════════════════════════════════════════════════════════════════════

alter table seo_sem.metricas_mes add column if not exists desde date;
alter table seo_sem.metricas_mes add column if not exists hasta date;
alter table seo_sem.metricas_mes add column if not exists dias integer;

create table if not exists seo_sem.metricas_grupo_mes (
  id            uuid primary key default gen_random_uuid(),
  grupo_id      uuid not null references seo_sem.grupos (id) on delete cascade,
  campana_id    uuid not null references seo_sem.campanas (id) on delete cascade,
  mes           text not null,                        -- 'AAAA-MM'
  coste         numeric not null default 0,
  clics         integer not null default 0,
  impresiones   integer not null default 0,
  conversiones  numeric not null default 0,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  unique (grupo_id, mes)
);
drop trigger if exists set_updated_at on seo_sem.metricas_grupo_mes;
create trigger set_updated_at before update on seo_sem.metricas_grupo_mes for each row execute function seo_sem.set_updated_at();
create index if not exists metricas_grupo_mes_campana_idx on seo_sem.metricas_grupo_mes (campana_id, mes);

grant all on seo_sem.metricas_grupo_mes to anon, authenticated, service_role;
alter table seo_sem.metricas_grupo_mes enable row level security;
drop policy if exists "grupo acceso total" on seo_sem.metricas_grupo_mes;
create policy "grupo acceso total" on seo_sem.metricas_grupo_mes for all to authenticated
  using (seo_sem.es_del_grupo()) with check (seo_sem.es_del_grupo());

notify pgrst, 'reload schema';
