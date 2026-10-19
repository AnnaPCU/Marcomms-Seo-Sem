-- ════════════════════════════════════════════════════════════════════
-- 0006_historico_cuentas.sql — Marcomms SEO-SEM
-- Histórico de Google Ads de dos cuentas: la actual («Control Union - (en ARG)», en pesos, desde jul 2026) y la
-- anterior («Peterson Technologies», en euros, campañas CU y PS de feb a jul 2026). Las dos cuentas repiten nombres
-- de campaña, así que el nombre pasa a ser único por cuenta. El gasto se guarda siempre en pesos; las filas que
-- vienen en otra moneda conservan el importe original y el tipo de cambio usado (BCRA, promedio del mes).
-- Lo carga scripts/publicar.py --solo historico desde informe/datos_ads_historico.json (ads_historico.py).
-- Idempotente. Solo toca el esquema seo_sem.
-- ════════════════════════════════════════════════════════════════════

alter table seo_sem.campanas add column if not exists cuenta text not null default 'actual';
alter table seo_sem.campanas drop constraint if exists campanas_cuenta_check;
alter table seo_sem.campanas add constraint campanas_cuenta_check check (cuenta in ('actual', 'anterior'));
alter table seo_sem.campanas drop constraint if exists campanas_nombre_key;
alter table seo_sem.campanas drop constraint if exists campanas_cuenta_nombre_key;
alter table seo_sem.campanas add constraint campanas_cuenta_nombre_key unique (cuenta, nombre);

alter table seo_sem.metricas_mes add column if not exists moneda_original text;
alter table seo_sem.metricas_mes add column if not exists coste_original numeric;
alter table seo_sem.metricas_mes add column if not exists tipo_cambio numeric;

notify pgrst, 'reload schema';
