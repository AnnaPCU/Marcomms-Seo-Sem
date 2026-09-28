/** Últimas corridas de extracción por fuente, y métricas mensuales por campaña. */
import { supabase } from '@/lib/supabase';
import type { ExtraccionRow, Fuente, MetricaMesRow } from '@/lib/database.types';

export interface Extraccion {
  id: string;
  fuente: Fuente;
  corridaEn: string;
  desde: string | null;
  hasta: string | null;
  filas: number | null;
  detalle: Record<string, unknown>;
}
export interface MetricaMes {
  campanaId: string;
  mes: string;
  coste: number;
  clics: number;
  impresiones: number;
  conversiones: number;
}

const extraccionFromRow = (r: ExtraccionRow): Extraccion => ({
  id: r.id,
  fuente: r.fuente,
  corridaEn: r.corrida_en,
  desde: r.desde,
  hasta: r.hasta,
  filas: r.filas,
  detalle: (r.detalle && typeof r.detalle === 'object' && !Array.isArray(r.detalle) ? r.detalle : {}) as Record<string, unknown>,
});
const metricaFromRow = (r: MetricaMesRow): MetricaMes => ({
  campanaId: r.campana_id,
  mes: r.mes,
  coste: Number(r.coste),
  clics: r.clics,
  impresiones: r.impresiones,
  conversiones: Number(r.conversiones),
});

/** La corrida más reciente de cada fuente. */
export async function ultimasExtracciones(): Promise<Record<Fuente, Extraccion | null>> {
  const { data, error } = await supabase.from('extracciones').select('*').order('corrida_en', { ascending: false }).limit(50);
  if (error) throw error;
  const salida: Record<Fuente, Extraccion | null> = { search_console: null, google_ads: null };
  for (const row of data ?? []) {
    const e = extraccionFromRow(row);
    if (!salida[e.fuente]) salida[e.fuente] = e;
  }
  return salida;
}

export async function listarMetricas(): Promise<MetricaMes[]> {
  const { data, error } = await supabase.from('metricas_mes').select('*').order('mes', { ascending: false });
  if (error) throw error;
  return (data ?? []).map(metricaFromRow);
}
