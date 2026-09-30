/**
 * Seguimiento del presupuesto total: cuánto hay asignado en el mes, cuánto se gastó, a qué ritmo, y de dónde a dónde
 * conviene rotar inversión (campañas topeadas por presupuesto vs. campañas con presupuesto ocioso).
 */
import { AlertTriangle, ArrowDownRight, ArrowUpRight, CircleSlash } from 'lucide-react';
import { Kpi, Tarjeta } from '@/components/shared/Ui';
import { ars, campanaCorta } from '@/utils/formato';
import { UMBRAL_OCIOSO, UMBRAL_TOPE, type FilaRotacion, type Resumen } from '@/utils/presupuesto';
import { BarraConsumo } from './Semaforo';

function Lista({ filas, vacio, tipo }: { filas: FilaRotacion[]; vacio: string; tipo: 'tope' | 'ocio' }) {
  if (!filas.length) return <p className="text-sm text-mc-grey">{vacio}</p>;
  return (
    <ul className="space-y-1.5">
      {filas.slice(0, 8).map((f) => (
        <li key={f.campanaId} className="flex items-center justify-between gap-3 text-[13px]">
          <span className="truncate text-mc-navy" title={f.nombre}>
            <span className="mr-1.5 rounded bg-mc-navy px-1 py-0.5 text-[10px] font-semibold text-white">{f.marca}</span>
            {campanaCorta(f.nombre)}
          </span>
          <span className="shrink-0 font-mono text-xs">
            <span className={tipo === 'tope' ? 'text-red-700' : 'text-mc-grey'}>{Math.round(f.ritmo * 100)}%</span>
            <span className="ml-2 text-mc-grey">{tipo === 'ocio' ? `sobran ${ars(f.margenDia)}/día` : f.margenDia < 0 ? `+${ars(-f.margenDia)}/día` : 'al tope'}</span>
          </span>
        </li>
      ))}
      {filas.length > 8 && <li className="text-xs text-mc-grey">y {filas.length - 8} más</li>}
    </ul>
  );
}

export default function PanelRotacion({ r, dias, diasMes, hasta }: { r: Resumen; dias: number; diasMes: number; hasta: string | null }) {
  const desvioProyeccion = r.presMes > 0 ? r.proyeccion / r.presMes : null;
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        <Kpi valor={ars(r.presMes)} etiqueta="Presupuesto del mes" nota={`${ars(r.presDia)} por día en campañas activas × ${diasMes} días`} />
        <Kpi valor={ars(r.gasto)} etiqueta={`Gastado al día ${dias}`} nota={`${ars(r.gastoDia)} por día · ${r.presDia ? Math.round((r.gastoDia / r.presDia) * 100) : 0}% del ritmo asignado`} />
        <Kpi valor={ars(r.proyeccion)} etiqueta="Proyección al cierre" nota={desvioProyeccion !== null ? `${Math.round(desvioProyeccion * 100)}% del presupuesto del mes al ritmo actual` : undefined} />
        <Kpi valor={ars(r.disponible)} etiqueta="Presupuesto sin usar" nota={`${ars(r.sobranteDia)} por día ocioso en ${r.ociosas.length} campañas`} />
      </div>

      <Tarjeta className="px-4 py-3">
        <div className="mb-2 flex items-baseline justify-between">
          <span className="text-[11px] font-semibold uppercase tracking-[0.12em] text-mc-grey">Consumo total del mes</span>
          <span className="text-xs text-mc-grey">la línea marca dónde debería estar al {hasta ? `día ${dias}` : 'día de hoy'} ({Math.round(r.esperado * 100)}%)</span>
        </div>
        <BarraConsumo valor={r.consumo} semaforo={r.consumo !== null && r.consumo > r.esperado * 1.05 ? 'rojo' : 'verde'} marca={r.esperado} />
      </Tarjeta>

      <div className="flex flex-wrap gap-2 text-[13px]">
        <span className="inline-flex items-center gap-1.5 rounded-lg bg-red-50 px-3 py-1.5 text-red-800 ring-1 ring-red-200">
          <AlertTriangle size={14} /> {r.sobre.length} {r.sobre.length === 1 ? 'campaña gasta' : 'campañas gastan'} más de un 5% por encima de su presupuesto
        </span>
        <span className="inline-flex items-center gap-1.5 rounded-lg bg-red-50 px-3 py-1.5 text-red-800 ring-1 ring-red-200">
          <CircleSlash size={14} /> {r.sinGasto.length} {r.sinGasto.length === 1 ? 'campaña activa no gasta' : 'campañas activas no gastan'} nada
        </span>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Tarjeta className="p-4">
          <h3 className="mb-1 flex items-center gap-1.5 text-sm">
            <ArrowUpRight size={16} className="text-red-600" /> Topeadas: piden más presupuesto
          </h3>
          <p className="mb-3 text-xs text-mc-grey">Gastan el {Math.round(UMBRAL_TOPE * 100)}% o más de lo asignado por día. Si convierten o tienen buena relevancia, son las candidatas a recibir inversión.</p>
          <Lista filas={r.topeadas} vacio="Ninguna campaña está limitada por presupuesto." tipo="tope" />
        </Tarjeta>
        <Tarjeta className="p-4">
          <h3 className="mb-1 flex items-center gap-1.5 text-sm">
            <ArrowDownRight size={16} className="text-mc-blue" /> Con presupuesto ocioso: de dónde sacarlo
          </h3>
          <p className="mb-3 text-xs text-mc-grey">Gastan menos del {Math.round(UMBRAL_OCIOSO * 100)}% de lo asignado. Ese sobrante se puede mover a las topeadas sin subir el total.</p>
          <Lista filas={r.ociosas} vacio="No hay presupuesto ocioso." tipo="ocio" />
        </Tarjeta>
      </div>
    </div>
  );
}
