/** Gasto mensual por campaña y por grupo de anuncios (lo carga scripts/publicar.py). */
import { supabase } from '@/lib/supabase';
import type { MetricaGrupoMesRow, MetricaMesRow } from '@/lib/database.types';

export interface MetricaMes {
  campanaId: string;
  mes: string;
  desde: string | null;
  hasta: string | null;
  dias: number | null;
  coste: number;
  clics: number;
  impresiones: number;
  conversiones: number;
}

export interface MetricaGrupoMes {
  grupoId: string;
  campanaId: string;
  mes: string;
  coste: number;
  clics: number;
  impresiones: number;
  conversiones: number;
}

const metricaFromRow = (r: MetricaMesRow): MetricaMes => ({
  campanaId: r.campana_id,
  mes: r.mes,
  desde: r.desde,
  hasta: r.hasta,
  dias: r.dias,
  coste: Number(r.coste),
  clics: r.clics,
  impresiones: r.impresiones,
  conversiones: Number(r.conversiones),
});

const metricaGrupoFromRow = (r: MetricaGrupoMesRow): MetricaGrupoMes => ({
  grupoId: r.grupo_id,
  campanaId: r.campana_id,
  mes: r.mes,
  coste: Number(r.coste),
  clics: r.clics,
  impresiones: r.impresiones,
  conversiones: Number(r.conversiones),
});

export async function listarMetricas(): Promise<MetricaMes[]> {
  const { data, error } = await supabase.from('metricas_mes').select('*').order('mes', { ascending: false });
  if (error) throw error;
  return (data ?? []).map(metricaFromRow);
}

export async function listarMetricasGrupo(): Promise<MetricaGrupoMes[]> {
  const { data, error } = await supabase.from('metricas_grupo_mes').select('*').order('mes', { ascending: false });
  if (error) throw error;
  return (data ?? []).map(metricaGrupoFromRow);
}
