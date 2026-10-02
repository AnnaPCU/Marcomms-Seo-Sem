/**
 * Estados del tablero y sus etiquetas. Un solo lugar para el orden de columnas y los textos.
 */
import type { Estado, Marca, Prioridad, Tipo } from '@/lib/database.types';

// Color de cada columna: franja superior, punto y fondo de la cabecera.
export const ESTADOS: { id: Estado; label: string; hint: string; franja: string; punto: string; fondo: string }[] = [
  { id: 'propuesta', label: 'Propuesta', hint: 'Lo que el análisis recomienda y todavía nadie tomó', franja: 'border-t-mc-blue', punto: 'bg-mc-blue', fondo: 'bg-sky-50' },
  { id: 'en_proceso', label: 'En proceso', hint: 'Alguien la está aplicando', franja: 'border-t-mc-gold', punto: 'bg-mc-gold', fondo: 'bg-amber-50' },
  { id: 'hecha', label: 'Hecha', hint: 'Aplicada. La API la verifica al mes siguiente', franja: 'border-t-mc-green', punto: 'bg-mc-green', fondo: 'bg-emerald-50' },
  { id: 'descartada', label: 'Descartada', hint: 'Se decidió no hacerla; queda el motivo', franja: 'border-t-mc-grey', punto: 'bg-mc-grey', fondo: 'bg-mc-tint' },
];
export const ESTADO_BY_ID = Object.fromEntries(ESTADOS.map((e) => [e.id, e])) as Record<Estado, (typeof ESTADOS)[number]>;

export const MARCAS: { id: Marca; label: string; corto: string }[] = [
  { id: 'CU', label: 'Control Union', corto: 'CU' },
  { id: 'PCU', label: 'Peterson Control Union (ISO)', corto: 'PCU' },
  { id: 'PS', label: 'Peterson Solutions', corto: 'PS' },
];
export const MARCA_BY_ID = Object.fromEntries(MARCAS.map((m) => [m.id, m])) as Record<Marca, (typeof MARCAS)[number]>;

export const TIPOS: { id: Tipo; label: string }[] = [
  { id: 'SEM', label: 'SEM · campañas' },
  { id: 'SEO', label: 'SEO · sitios' },
];

// Semáforo de prioridad: rojo, ámbar y verde de Tailwind. El ámbar no es el amarillo de Peterson (#f1e747).
export const PRIORIDADES: { id: Prioridad; label: string; clase: string; borde: string; punto: string }[] = [
  { id: 'alta', label: 'Alta', clase: 'bg-red-100 text-red-800', borde: 'border-l-red-500', punto: 'bg-red-500' },
  { id: 'media', label: 'Media', clase: 'bg-amber-100 text-amber-800', borde: 'border-l-amber-400', punto: 'bg-amber-400' },
  { id: 'baja', label: 'Baja', clase: 'bg-emerald-100 text-emerald-800', borde: 'border-l-emerald-500', punto: 'bg-emerald-500' },
];
export const PRIORIDAD_BY_ID = Object.fromEntries(PRIORIDADES.map((p) => [p.id, p])) as Record<Prioridad, (typeof PRIORIDADES)[number]>;

/**
 * Tipo de mejora de las tarjetas SEM (evidencia.acciones, lo calcula exportar_recomendaciones.py según lo que la mejora
 * pide hacer). Una tarjeta puede tener varios.
 */
export const ACCIONES: { id: string; label: string; corto: string }[] = [
  { id: 'anuncio', label: 'Anuncio (títulos y descripciones)', corto: 'Anuncio' },
  { id: 'keywords', label: 'Palabras clave', corto: 'Keywords' },
  { id: 'negativas', label: 'Negativas', corto: 'Negativas' },
  { id: 'estructura', label: 'Grupos y campañas', corto: 'Estructura' },
  { id: 'pausa', label: 'Pausar o presupuesto', corto: 'Pausa / CPC' },
  { id: 'landing', label: 'Landing y páginas', corto: 'Landing' },
  { id: 'revisar', label: 'Revisar o decidir', corto: 'Revisar' },
];
export const ACCION_BY_ID = Object.fromEntries(ACCIONES.map((a) => [a.id, a])) as Record<string, (typeof ACCIONES)[number]>;

/** Tipos de mejora de una tarjeta, en el orden de ACCIONES. */
export function accionesDe(evidencia: Record<string, unknown>): string[] {
  const a = evidencia.acciones;
  return Array.isArray(a) ? ACCIONES.map((x) => x.id).filter((id) => a.includes(id)) : [];
}

// Dominios que aceptan las políticas RLS del esquema (seo_sem.es_del_grupo).
export const DOMINIOS_PERMITIDOS = ['onepeterson.com', 'controlunion.com'];
