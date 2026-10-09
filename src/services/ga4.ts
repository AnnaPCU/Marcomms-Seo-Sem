/** Métricas limpias de Google Analytics 4 por sitio y mes (las carga scripts/publicar.py desde ga4_export.py). */
import { supabase } from '@/lib/supabase';
import type { Ga4SitioMesRow, Marca } from '@/lib/database.types';

export interface Ga4Landing {
  pagina: string;
  sesiones: number;
  interaccion: number;
}

export interface Ga4Datos {
  sesiones: number;
  interaccion: number; // sesiones con interacción (engagedSessions): descuenta rebotes y bots
  usuarios: number;
  vistas: number;
  duracion_media: number; // segundos
  canales: Record<string, { sesiones: number; interaccion: number }>;
  contactos: Record<string, { formularios: number; emails: number }>;
  contactos_total: number;
  directo_sin_interaccion: number;
  landings_pagas: Ga4Landing[];
  landings_organicas: Ga4Landing[];
}

export interface Ga4SitioMes {
  sitio: string; // 'espana.controlunion.com'
  marca: Marca;
  nombre: string;
  mes: string; // 'AAAA-MM'
  desde: string;
  hasta: string;
  dias: number;
  datos: Ga4Datos;
}

const VACIO: Ga4Datos = {
  sesiones: 0, interaccion: 0, usuarios: 0, vistas: 0, duracion_media: 0, canales: {}, contactos: {}, contactos_total: 0,
  directo_sin_interaccion: 0, landings_pagas: [], landings_organicas: [],
};

export const ga4FromRow = (r: Ga4SitioMesRow): Ga4SitioMes => ({
  sitio: r.sitio,
  marca: r.marca,
  nombre: r.nombre,
  mes: r.mes,
  desde: r.desde,
  hasta: r.hasta,
  dias: r.dias,
  datos: { ...VACIO, ...(r.datos as unknown as Partial<Ga4Datos>) },
});

export async function listarGa4(): Promise<Ga4SitioMes[]> {
  const { data, error } = await supabase.from('ga4_sitio_mes').select('*').order('mes', { ascending: false }).order('nombre');
  if (error) throw error;
  return (data ?? []).map(ga4FromRow);
}
