-- ════════════════════════════════════════════════════════════════════
-- 0007_cambios_ads.sql — Marcomms SEO-SEM
-- Historial de cambios de Google Ads (change_event) por campaña, para la vista «Impacto»: qué se cargó de verdad
-- (keywords, negativas, pausas, anuncios, grupos, presupuesto) y cuándo, para cruzarlo con los ítems de cada tarjeta
-- y medir antes / después desde la fecha real del cambio.
-- Lo carga scripts/publicar.py --solo cambios desde informe/datos_cambios_ads.json (ads_cambios.py del proyecto de análisis).
-- Google guarda solo 30 días: la carga es idempotente por evento_id y se acumula acá.
-- No guarda quién hizo el cambio. Idempotente. Solo toca el esquema seo_sem.
-- ════════════════════════════════════════════════════════════════════

create table if not exists seo_sem.cambios_ads (
  evento_id   text primary key,
  campana_id  uuid not null references seo_sem.campanas (id) on delete cascade,
  fecha       timestamp not null,          -- hora de la cuenta de Ads (Argentina)
  recurso     text not null,               -- AD_GROUP_CRITERION, CAMPAIGN_CRITERION, AD, AD_GROUP_AD, AD_GROUP, CAMPAIGN_BUDGET, CAMPAIGN…
  operacion   text not null,               -- CREATE, UPDATE, REMOVE
  grupo       text,
  origen      text,                        -- interfaz web, Editor o API
  campos      text,
  detalle     jsonb not null default '{}'::jsonb,
  resumen     text not null,
  created_at  timestamptz not null default now()
);
create index if not exists cambios_ads_campana_fecha_idx on seo_sem.cambios_ads (campana_id, fecha);

grant all on seo_sem.cambios_ads to anon, authenticated, service_role;
alter table seo_sem.cambios_ads enable row level security;
drop policy if exists "grupo acceso total" on seo_sem.cambios_ads;
create policy "grupo acceso total" on seo_sem.cambios_ads for all to authenticated
  using (seo_sem.es_del_grupo()) with check (seo_sem.es_del_grupo());

notify pgrst, 'reload schema';
