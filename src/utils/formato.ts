/** Formateadores compartidos. Sin dependencias; se testean en formato.test.ts. */

export function ars(valor: number | null | undefined): string {
  if (valor === null || valor === undefined || Number.isNaN(valor)) return '—';
  return 'ARS ' + Math.round(valor).toLocaleString('es-AR');
}

export function entero(valor: number | null | undefined): string {
  if (valor === null || valor === undefined || Number.isNaN(valor)) return '—';
  return Math.round(valor).toLocaleString('es-AR');
}

export function pct(parte: number, total: number, decimales = 0): string {
  if (!total) return '—';
  return ((parte / total) * 100).toFixed(decimales) + '%';
}

/** '2026-09-28T17:10:00Z' → '28 sep 2026, 14:10' en hora local. */
export function fechaHora(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleString('es-AR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

/** '2026-09-14' → '14 sep 2026'. */
export function fecha(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso.length === 10 ? iso + 'T00:00:00' : iso);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' });
}

/** '2026-09' → 'sep 2026'. */
export function mesCorto(aaaaMm: string | null | undefined): string {
  if (!aaaaMm || !/^\d{4}-\d{2}$/.test(aaaaMm)) return '—';
  const [a, m] = aaaaMm.split('-').map(Number);
  return new Date(a, m - 1, 1).toLocaleDateString('es-AR', { month: 'short', year: 'numeric' });
}

/** Mes actual como 'AAAA-MM'. */
export function mesActual(hoy = new Date()): string {
  return `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}`;
}

/** Días transcurridos desde una fecha ISO; null si no hay fecha. */
export function diasDesde(iso: string | null | undefined, hoy = new Date()): number | null {
  if (!iso) return null;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return null;
  return Math.floor((hoy.getTime() - d.getTime()) / 86_400_000);
}

/** Quita el sufijo " - Search" de los nombres de campaña de la cuenta. */
export function campanaCorta(nombre: string): string {
  return nombre.replace(/\s*-\s*search\s*$/i, '');
}
