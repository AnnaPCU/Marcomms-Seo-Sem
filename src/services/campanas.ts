/** Catálogo de campañas y grupos (lo sincroniza scripts/publicar.py desde la API de Google Ads). */
import { supabase } from '@/lib/supabase';
import type { CampanaRow, GrupoRow, Marca } from '@/lib/database.types';

export interface Campana {
  id: string;
  adsId: string | null;
  nombre: string;
  marca: Marca;
  unidad: string;
  estado: string;
  presupuestoDia: number | null;
  creadaEnCuenta: boolean;
}
export interface Grupo {
  id: string;
  campanaId: string;
  nombre: string;
  estado: string;
}

export const campanaFromRow = (r: CampanaRow): Campana => ({
  id: r.id,
  adsId: r.ads_id,
  nombre: r.nombre,
  marca: r.marca,
  unidad: r.unidad,
  estado: r.estado,
  presupuestoDia: r.presupuesto_dia === null ? null : Number(r.presupuesto_dia),
  creadaEnCuenta: Boolean(r.creada_en_cuenta),
});
export const grupoFromRow = (r: GrupoRow): Grupo => ({ id: r.id, campanaId: r.campana_id, nombre: r.nombre, estado: r.estado });

export async function listarCampanas(): Promise<Campana[]> {
  const { data, error } = await supabase.from('campanas').select('*').order('marca').order('unidad').order('nombre');
  if (error) throw error;
  return (data ?? []).map(campanaFromRow);
}

export async function listarGrupos(): Promise<Grupo[]> {
  const { data, error } = await supabase.from('grupos').select('*').order('nombre');
  if (error) throw error;
  return (data ?? []).map(grupoFromRow);
}
