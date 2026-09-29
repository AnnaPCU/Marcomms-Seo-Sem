/**
 * Estados del tablero y sus etiquetas. Un solo lugar para el orden de columnas y los textos.
 */
import type { Estado, Marca, Prioridad, Tipo } from '@/lib/database.types';

export const ESTADOS: { id: Estado; label: string; hint: string }[] = [
  { id: 'propuesta', label: 'Propuesta', hint: 'Lo que el análisis recomienda y todavía nadie tomó' },
  { id: 'en_proceso', label: 'En proceso', hint: 'Alguien la está aplicando' },
  { id: 'hecha', label: 'Hecha', hint: 'Aplicada. La API la verifica al mes siguiente' },
  { id: 'descartada', label: 'Descartada', hint: 'Se decidió no hacerla; queda el motivo' },
];
export const ESTADO_BY_ID = Object.fromEntries(ESTADOS.map((e) => [e.id, e])) as Record<Estado, (typeof ESTADOS)[number]>;

export const MARCAS: { id: Marca; label: string; corto: string }[] = [
  { id: 'CU', label: 'Control Union', corto: 'CU' },
  { id: 'PCU', label: 'ISO 27001 (campañas «PCU»)', corto: 'PCU' },
  { id: 'PS', label: 'Peterson Solutions', corto: 'PS' },
];
export const MARCA_BY_ID = Object.fromEntries(MARCAS.map((m) => [m.id, m])) as Record<Marca, (typeof MARCAS)[number]>;

export const TIPOS: { id: Tipo; label: string }[] = [
  { id: 'SEM', label: 'SEM · campañas' },
  { id: 'SEO', label: 'SEO · sitios' },
];

export const PRIORIDADES: { id: Prioridad; label: string; clase: string }[] = [
  { id: 'alta', label: 'Alta', clase: 'bg-mc-navy text-white' },
  { id: 'media', label: 'Media', clase: 'bg-mc-tint2 text-mc-navy' },
  { id: 'baja', label: 'Baja', clase: 'bg-white text-mc-grey border border-mc-hair' },
];
export const PRIORIDAD_BY_ID = Object.fromEntries(PRIORIDADES.map((p) => [p.id, p])) as Record<Prioridad, (typeof PRIORIDADES)[number]>;

// Dominios que aceptan las políticas RLS del esquema (seo_sem.es_del_grupo).
export const DOMINIOS_PERMITIDOS = ['onepeterson.com', 'controlunion.com'];
