/**
 * Servicio de recomendaciones: la única capa que habla con la tabla `recomendaciones`.
 * Patrón MarComms Hub: fromRow / toRow, funciones puras async, sin estado de React.
 */
import { supabase } from '@/lib/supabase';
import type { Estado, Marca, RecomendacionEventoRow, RecomendacionRow, Tipo } from '@/lib/database.types';

export interface Recomendacion {
  id: string;
  clave: string;
  marca: Marca;
  tipo: Tipo;
  campanaId: string | null;
  grupoId: string | null;
  sitio: string | null;
  pagina: string | null;
  titulo: string;
  detalle: string;
  evidencia: Record<string, unknown>;
  prioridad: RecomendacionRow['prioridad'];
  estado: Estado;
  mesAlta: string;
  mesCierre: string | null;
  motivoDescarte: string | null;
  verificadaApi: boolean;
  verificadaEn: string | null;
  origen: string | null;
  orden: number;
  actualizadaPor: string | null;
  updatedAt: string;
}

export interface Evento {
  id: string;
  recomendacionId: string;
  deEstado: string | null;
  aEstado: string;
  motivo: string | null;
  usuario: string | null;
  creadoEn: string;
}

export function fromRow(r: RecomendacionRow): Recomendacion {
  return {
    id: r.id,
    clave: r.clave,
    marca: r.marca,
    tipo: r.tipo,
    campanaId: r.campana_id,
    grupoId: r.grupo_id,
    sitio: r.sitio,
    pagina: r.pagina,
    titulo: r.titulo,
    detalle: r.detalle,
    evidencia: (r.evidencia && typeof r.evidencia === 'object' && !Array.isArray(r.evidencia) ? r.evidencia : {}) as Record<string, unknown>,
    prioridad: r.prioridad,
    estado: r.estado,
    mesAlta: r.mes_alta,
    mesCierre: r.mes_cierre,
    motivoDescarte: r.motivo_descarte,
    verificadaApi: r.verificada_api,
    verificadaEn: r.verificada_en,
    origen: r.origen,
    orden: r.orden,
    actualizadaPor: r.actualizada_por,
    updatedAt: r.updated_at,
  };
}

export function eventoFromRow(r: RecomendacionEventoRow): Evento {
  return { id: r.id, recomendacionId: r.recomendacion_id, deEstado: r.de_estado, aEstado: r.a_estado, motivo: r.motivo, usuario: r.usuario, creadoEn: r.created_at };
}

export async function listarRecomendaciones(tipo?: Tipo): Promise<Recomendacion[]> {
  let q = supabase.from('recomendaciones').select('*').order('orden', { ascending: true }).order('created_at', { ascending: true });
  if (tipo) q = q.eq('tipo', tipo);
  const { data, error } = await q;
  if (error) throw error;
  return (data ?? []).map(fromRow);
}

/** Cambia el estado, deja el evento y cierra el mes si corresponde. */
export async function cambiarEstado(rec: Recomendacion, aEstado: Estado, usuario: string | null, motivo?: string): Promise<void> {
  if (rec.estado === aEstado) return;
  const mes = new Date();
  const mesCierre = `${mes.getFullYear()}-${String(mes.getMonth() + 1).padStart(2, '0')}`;
  const cierra = aEstado === 'hecha' || aEstado === 'descartada';
  const { error } = await supabase
    .from('recomendaciones')
    .update({
      estado: aEstado,
      mes_cierre: cierra ? mesCierre : null,
      motivo_descarte: aEstado === 'descartada' ? (motivo ?? null) : null,
      actualizada_por: usuario,
    })
    .eq('id', rec.id);
  if (error) throw error;
  const { error: e2 } = await supabase
    .from('recomendacion_eventos')
    .insert({ recomendacion_id: rec.id, de_estado: rec.estado, a_estado: aEstado, motivo: motivo ?? null, usuario });
  if (e2) throw e2;
}

/** Guarda el orden de varias tarjetas dentro de una columna. */
export async function reordenar(ids: string[]): Promise<void> {
  await Promise.all(ids.map((id, i) => supabase.from('recomendaciones').update({ orden: i }).eq('id', id)));
}

export async function listarEventos(recomendacionId?: string, limite = 200): Promise<Evento[]> {
  let q = supabase.from('recomendacion_eventos').select('*').order('created_at', { ascending: false }).limit(limite);
  if (recomendacionId) q = q.eq('recomendacion_id', recomendacionId);
  const { data, error } = await q;
  if (error) throw error;
  return (data ?? []).map(eventoFromRow);
}

/** Suscripción realtime: llama a `cb` ante cualquier cambio en la tabla. Devuelve la función para cancelar. */
export function suscribirRecomendaciones(cb: () => void): () => void {
  const canal = supabase
    .channel('recomendaciones-cambios')
    .on('postgres_changes', { event: '*', schema: 'public', table: 'recomendaciones' }, cb)
    .subscribe();
  return () => {
    void supabase.removeChannel(canal);
  };
}
