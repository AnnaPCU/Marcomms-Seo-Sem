/** Historial de cambios de Google Ads por campaña (change_event; lo carga scripts/publicar.py --solo cambios). */
import { supabase } from '@/lib/supabase';
import type { CambioAdsRow } from '@/lib/database.types';

/** Lo que importa de cada cambio. Solo vienen los campos que aplican al tipo de recurso. */
export interface DetalleCambio {
  texto?: string;
  concordancia?: 'exacta' | 'frase' | 'amplia';
  negativa?: boolean;
  estado_antes?: string;
  estado_despues?: string;
  nombre?: string;
  anuncio_id?: string;
  titulos_agregados?: string[];
  titulos_quitados?: string[];
  descripciones_agregadas?: string[];
  descripciones_quitadas?: string[];
  urls_despues?: string[];
  presupuesto_antes?: number;
  presupuesto_despues?: number;
}

export interface CambioAds {
  id: string;
  campanaId: string;
  /** Hora de la cuenta de Ads, 'AAAA-MM-DDTHH:MM:SS'. */
  fecha: string;
  recurso: string;
  operacion: 'CREATE' | 'UPDATE' | 'REMOVE' | string;
  grupo: string | null;
  detalle: DetalleCambio;
  resumen: string;
}

function desdeFila(r: CambioAdsRow): CambioAds {
  return {
    id: r.evento_id,
    campanaId: r.campana_id,
    fecha: r.fecha,
    recurso: r.recurso,
    operacion: r.operacion,
    grupo: r.grupo,
    detalle: (r.detalle ?? {}) as DetalleCambio,
    resumen: r.resumen,
  };
}

export async function listarCambiosAds(): Promise<CambioAds[]> {
  const filas: CambioAdsRow[] = [];
  for (let i = 0; ; i += 1000) {
    const { data, error } = await supabase.from('cambios_ads').select('*').order('fecha').range(i, i + 999);
    if (error) throw error;
    filas.push(...(data ?? []));
    if (!data || data.length < 1000) break;
  }
  return filas.map(desdeFila);
}
