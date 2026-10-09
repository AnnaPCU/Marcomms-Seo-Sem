-- ════════════════════════════════════════════════════════════════════
-- 0005_ga4_sitio_mes.sql — Marcomms SEO-SEM
-- Métricas limpias de Google Analytics 4 por sitio y por mes, para la pestaña «Sitios»:
-- visitas con interacción (descuenta bots), canales, contactos reales (formularios del sitio + emails que no son de
-- empleo/academia/reclamos) y páginas de entrada pagas y orgánicas. Lo carga scripts/publicar.py desde
-- informe/datos_ga4.json (ga4_export.py del proyecto de análisis). `datos` guarda el detalle tal como sale del script.
-- Idempotente. Solo toca el esquema seo_sem.
-- ════════════════════════════════════════════════════════════════════

create table if not exists seo_sem.ga4_sitio_mes (
  id          uuid primary key default gen_random_uuid(),
  sitio       text not null,                 -- 'espana.controlunion.com'
  marca       text not null check (marca in ('CU', 'PS', 'PCU')),
  nombre      text not null,
  propiedad   text not null,                 -- 'properties/512083164'
  mes         text not null,                 -- 'AAAA-MM'
  desde       date not null,
  hasta       date not null,
  dias        integer not null,
  datos       jsonb not null,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  unique (sitio, mes)
);
drop trigger if exists set_updated_at on seo_sem.ga4_sitio_mes;
create trigger set_updated_at before update on seo_sem.ga4_sitio_mes for each row execute function seo_sem.set_updated_at();

grant all on seo_sem.ga4_sitio_mes to anon, authenticated, service_role;
alter table seo_sem.ga4_sitio_mes enable row level security;
drop policy if exists "grupo acceso total" on seo_sem.ga4_sitio_mes;
create policy "grupo acceso total" on seo_sem.ga4_sitio_mes for all to authenticated
  using (seo_sem.es_del_grupo()) with check (seo_sem.es_del_grupo());

notify pgrst, 'reload schema';
