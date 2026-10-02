-- ════════════════════════════════════════════════════════════════════
-- 0004_metricas_dia.sql — Marcomms SEO-SEM
-- Gasto por campaña y por día, para la vista «Día a día» de Presupuesto: cada día contra el presupuesto diario.
-- Lo carga scripts/publicar.py desde informe/datos_gasto_diario.json (ads_diario.py del proyecto de análisis).
-- Google omite los días sin impresiones: un día sin fila es un día sin gasto.
-- Idempotente. Solo toca el esquema seo_sem.
-- ════════════════════════════════════════════════════════════════════

create table if not exists seo_sem.metricas_dia (
  id            uuid primary key default gen_random_uuid(),
  campana_id    uuid not null references seo_sem.campanas (id) on delete cascade,
  fecha         date not null,
  coste         numeric not null default 0,
  clics         integer not null default 0,
  impresiones   integer not null default 0,
  conversiones  numeric not null default 0,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  unique (campana_id, fecha)
);
drop trigger if exists set_updated_at on seo_sem.metricas_dia;
create trigger set_updated_at before update on seo_sem.metricas_dia for each row execute function seo_sem.set_updated_at();
create index if not exists metricas_dia_fecha_idx on seo_sem.metricas_dia (fecha);

grant all on seo_sem.metricas_dia to anon, authenticated, service_role;
alter table seo_sem.metricas_dia enable row level security;
drop policy if exists "grupo acceso total" on seo_sem.metricas_dia;
create policy "grupo acceso total" on seo_sem.metricas_dia for all to authenticated
  using (seo_sem.es_del_grupo()) with check (seo_sem.es_del_grupo());

notify pgrst, 'reload schema';
