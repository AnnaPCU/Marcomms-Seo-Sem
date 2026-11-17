/**
 * Actualizaciones de la revisión mensual: cuando la revisión ajusta una tarjeta en «propuesta» o «en proceso», agrega
 * una entrada en evidencia.revisiones ({mes, accion: 'ajuste', motivo, fecha}). El tablero la marca como «Actualizada»
 * hasta la revisión siguiente.
 */
import { diasDesde, mesActual } from './formato';

export interface Revision {
  mes: string;
  accion?: string;
  motivo?: string;
  fecha?: string;
  datos_hasta?: string;
}

/** Días que una tarjeta se muestra como «Actualizada» (un ciclo de revisión mensual). */
export const DIAS_RECIENTE = 35;

/** El último ajuste de la revisión mensual si es reciente; si no, null. Sin fecha, cuenta el del mes actual. */
export function actualizacionReciente(evidencia: Record<string, unknown>, hoy = new Date()): Revision | null {
  const revs = Array.isArray(evidencia.revisiones) ? (evidencia.revisiones as Revision[]) : [];
  const ultimo = [...revs].reverse().find((r) => r && r.accion === 'ajuste');
  if (!ultimo) return null;
  const dias = diasDesde(ultimo.fecha, hoy);
  if (dias !== null) return dias <= DIAS_RECIENTE ? ultimo : null;
  return ultimo.mes === mesActual(hoy) ? ultimo : null;
}
