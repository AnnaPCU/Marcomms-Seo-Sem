/** Piezas visuales del seguimiento de presupuesto: barra de consumo 0–100 y chip de semáforo. */
import type { Semaforo as TipoSemaforo } from '@/utils/presupuesto';

export const COLOR_SEMAFORO: Record<TipoSemaforo, { barra: string; chip: string; texto: string }> = {
  rojo: { barra: 'bg-gradient-to-r from-red-400 to-red-600', chip: 'bg-red-50 text-red-700 ring-1 ring-red-200', texto: 'text-red-700' },
  verde: { barra: 'bg-gradient-to-r from-emerald-400 to-emerald-600', chip: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200', texto: 'text-emerald-700' },
  gris: { barra: 'bg-mc-grey', chip: 'bg-mc-tint2 text-mc-grey', texto: 'text-mc-grey' },
};

/**
 * Barra de 0 a 100%. `valor` puede pasar de 1: la barra se llena y el número muestra el valor real.
 * `marca` dibuja una línea donde debería estar el consumo a esta altura del mes.
 */
export function BarraConsumo({ valor, semaforo, marca, alto }: { valor: number | null; semaforo: TipoSemaforo; marca?: number; alto?: boolean }) {
  if (valor === null) return <span className="text-xs text-mc-grey">sin presupuesto</span>;
  const ancho = Math.max(0, Math.min(valor, 1)) * 100;
  return (
    <div className="flex items-center gap-2">
      <div className={`relative flex-1 rounded-full bg-mc-tint2 ${alto ? 'h-3.5' : 'h-2'}`} title={`${Math.round(valor * 100)}% del presupuesto`}>
        <div className={`h-full rounded-full transition-[width] duration-700 ${COLOR_SEMAFORO[semaforo].barra}`} style={{ width: `${ancho}%` }} />
        {marca !== undefined && (
          <div className={`absolute w-0.5 rounded bg-mc-navy ${alto ? '-top-1.5 h-6' : '-top-1 h-4'}`} style={{ left: `calc(${Math.min(marca, 1) * 100}% - 1px)` }} title="Dónde debería estar hoy" />
        )}
      </div>
      <span className={`w-11 text-right font-mono font-semibold ${alto ? 'text-sm' : 'text-xs'} ${COLOR_SEMAFORO[semaforo].texto}`}>{Math.round(valor * 100)}%</span>
    </div>
  );
}

/** Chip de exceso («+8%»), de «sin gasto», o vacío si la campaña está dentro de su presupuesto. */
export function ChipDesvio({ coste, ritmo, estado }: { coste: number; ritmo: number | null; estado?: string }) {
  if (estado && estado !== 'ENABLED')
    return <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${COLOR_SEMAFORO.gris.chip}`}>{estado === 'REMOVED' ? 'eliminada' : 'pausada'}</span>;
  if (ritmo === null) return null;
  if (coste <= 0) return <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${COLOR_SEMAFORO.rojo.chip}`}>sin gasto</span>;
  if (ritmo > 1.05) return <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${COLOR_SEMAFORO.rojo.chip}`}>+{Math.round((ritmo - 1) * 100)}%</span>;
  return null;
}
