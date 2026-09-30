/**
 * Tipos de la base (esquema seo_sem). PROVISORIOS, escritos a mano a partir de supabase/migrations/0001_esquema.sql.
 * Cuando el proyecto de Supabase exista, se reemplazan por los generados:
 *   supabase gen types typescript --project-id cogdfbonpvvuzhurmvlq --schema seo_sem > src/lib/database.types.ts
 * Mantener la misma forma (Database.seo_sem.Tables.<tabla>.Row/Insert/Update) para que el reemplazo sea transparente.
 */
export type Marca = 'CU' | 'PS' | 'PCU';
export type Tipo = 'SEM' | 'SEO';
export type Prioridad = 'alta' | 'media' | 'baja';
export type Estado = 'propuesta' | 'en_proceso' | 'hecha' | 'descartada';
export type Fuente = 'search_console' | 'google_ads';

type Json = string | number | boolean | null | { [key: string]: Json } | Json[];

export type CampanaRow = {
  id: string; ads_id: string | null; nombre: string; marca: Marca; unidad: string; estado: string;
  presupuesto_dia: number | null; creada_en_cuenta: boolean | null; created_at: string; updated_at: string;
}
export type GrupoRow = {
  id: string; campana_id: string; ads_id: string | null; nombre: string; estado: string; created_at: string; updated_at: string;
}
export type RecomendacionRow = {
  id: string; clave: string; marca: Marca; tipo: Tipo; campana_id: string | null; grupo_id: string | null;
  sitio: string | null; pagina: string | null; titulo: string; detalle: string; evidencia: Json; prioridad: Prioridad;
  estado: Estado; mes_alta: string; mes_cierre: string | null; motivo_descarte: string | null; verificada_api: boolean;
  verificada_en: string | null; origen: string | null; orden: number; actualizada_por: string | null;
  created_at: string; updated_at: string;
}
export type RecomendacionEventoRow = {
  id: string; recomendacion_id: string; de_estado: string | null; a_estado: string; motivo: string | null; usuario: string | null; created_at: string;
}
export type ExtraccionRow = {
  id: string; fuente: Fuente; corrida_en: string; desde: string | null; hasta: string | null; filas: number | null; detalle: Json; created_at: string;
}
export type MetricaMesRow = {
  id: string; campana_id: string; mes: string; desde: string | null; hasta: string | null; dias: number | null; coste: number; clics: number; impresiones: number; conversiones: number; created_at: string; updated_at: string;
}
export type MetricaGrupoMesRow = {
  id: string; grupo_id: string; campana_id: string; mes: string; coste: number; clics: number; impresiones: number; conversiones: number; created_at: string; updated_at: string;
}

type Tabla<R> = { Row: R; Insert: Partial<R>; Update: Partial<R>; Relationships: never[] };

export interface Database {
  seo_sem: {
    Tables: {
      campanas: Tabla<CampanaRow>;
      grupos: Tabla<GrupoRow>;
      recomendaciones: Tabla<RecomendacionRow>;
      recomendacion_eventos: Tabla<RecomendacionEventoRow>;
      extracciones: Tabla<ExtraccionRow>;
      metricas_mes: Tabla<MetricaMesRow>;
      metricas_grupo_mes: Tabla<MetricaGrupoMesRow>;
    };
    Views: { [_ in never]: never };
    Functions: { [_ in never]: never };
    Enums: { [_ in never]: never };
    CompositeTypes: { [_ in never]: never };
  };
}
