/**
 * Seguimiento del presupuesto total: cuánto hay asignado en el mes, cuánto se gastó, a qué ritmo, cómo convierte,
 * y de dónde a dónde conviene rotar inversión (campañas topeadas vs. campañas con presupuesto ocioso).
 */
import { AlertTriangle, ArrowDownRight, ArrowUpRight, CircleSlash, Repeat } from 'lucide-react';
import { MARCA_BY_ID } from '@/constants/estados';
import { Kpi, PanelOscuro, Pildora, SeccionTitulo, Tarjeta } from '@/components/shared/Ui';
import { ars, campanaCorta, mesCorto } from '@/utils/formato';
import { consumoMes, semaforo, UMBRAL_OCIOSO, UMBRAL_TOPE, type FilaRotacion, type Nodo, type Resumen } from '@/utils/presupuesto';
import { BarraConsumo } from './Semaforo';
import Embudo from './Embudo';

function Lista({ filas, vacio, tipo }: { filas: FilaRotacion[]; vacio: string; tipo: 'tope' | 'ocio' }) {
  if (!filas.length) return <p className="text-sm text-mc-grey">{vacio}</p>;
  return (
    <ol className="space-y-1.5">
      {filas.slice(0, 8).map((f, i) => (
        <li key={f.campanaId} className="flex items-center gap-3 rounded-lg px-2 py-1.5 text-[13px] hover:bg-mc-tint">
          <span className={`grid h-5 w-5 shrink-0 place-items-center rounded-full text-[10px] font-bold text-white ${tipo === 'tope' ? 'bg-mc-red' : 'bg-mc-blue'}`}>{i + 1}</span>
          <span className="min-w-0 flex-1 truncate text-mc-navy" title={f.nombre}>
            <span className="mr-1.5 rounded bg-mc-navy px-1 py-0.5 text-[10px] font-semibold text-white">{f.marca}</span>
            {campanaCorta(f.nombre)}
          </span>
          <span className="shrink-0 font-mono text-xs">
            <span className={tipo === 'tope' ? 'font-semibold text-red-700' : 'text-mc-grey'}>{Math.round(f.ritmo * 100)}%</span>
            <span className="ml-2 text-mc-grey">{tipo === 'ocio' ? `sobran ${ars(f.margenDia)}/día` : f.margenDia < 0 ? `+${ars(-f.margenDia)}/día` : 'al tope'}</span>
          </span>
        </li>
      ))}
      {filas.length > 8 && <li className="px-2 text-xs text-mc-grey">y {filas.length - 8} más</li>}
    </ol>
  );
}

interface Props {
  r: Resumen;
  clientes: Nodo[];
  mes: string;
  dias: number;
  diasMes: number;
}

export default function PanelRotacion({ r, clientes, mes, dias, diasMes }: Props) {
  const ritmoTotal = r.presDia ? r.gastoDia / r.presDia : 0;
  const proyeccionRel = r.presMes > 0 ? r.proyeccion / r.presMes : 0;
  return (
    <div className="space-y-7">
      <section>
        <SeccionTitulo meta={`${mesCorto(mes)} · día ${dias} de ${diasMes}`}>Indicadores clave</SeccionTitulo>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
          <Kpi acento="noche" valor={ars(r.presMes)} etiqueta="Presupuesto del mes" nota={`${ars(r.presDia)} por día · campañas activas`} />
          <Kpi
            acento="azul"
            valor={ars(r.gasto)}
            etiqueta={`Gastado al día ${dias}`}
            pildora={<Pildora tono={ritmoTotal > 1.05 ? 'rojo' : 'azul'}>{Math.round(ritmoTotal * 100)}% del ritmo asignado</Pildora>}
            nota={`${ars(r.gastoDia)} por día`}
          />
          <Kpi
            acento={proyeccionRel > 1.05 ? 'rojo' : 'verde'}
            valor={ars(r.proyeccion)}
            etiqueta="Proyección al cierre"
            pildora={<Pildora tono={proyeccionRel > 1.05 ? 'rojo' : 'verde'}>{Math.round(proyeccionRel * 100)}% del presupuesto</Pildora>}
            nota="Al ritmo de gasto actual"
          />
          <Kpi
            acento="dorado"
            valor={ars(r.disponible)}
            etiqueta="Presupuesto sin usar"
            pildora={<Pildora tono="dorado">{ars(r.sobranteDia)}/día ocioso</Pildora>}
            nota={`en ${r.ociosas.length} campañas que gastan menos de la mitad`}
          />
        </div>
      </section>

      <section>
        <SeccionTitulo meta={`la línea marca dónde debería estar al día ${dias} (${Math.round(r.esperado * 100)}%)`}>Consumo del presupuesto</SeccionTitulo>
        <Tarjeta className="space-y-4 p-5">
          <div>
            <div className="mb-1.5 flex items-baseline justify-between">
              <span className="text-sm font-semibold text-mc-navy">Total de la cuenta</span>
              <span className="font-mono text-xs text-mc-grey">
                {ars(r.gasto)} de {ars(r.presMes)}
              </span>
            </div>
            <BarraConsumo valor={r.consumo} semaforo={r.consumo !== null && r.consumo > r.esperado * 1.05 ? 'rojo' : 'verde'} marca={r.esperado} alto />
          </div>
          <div className="grid grid-cols-1 gap-4 border-t border-mc-tint2 pt-4 md:grid-cols-3">
            {clientes.map((c) => (
              <div key={c.clave}>
                <div className="mb-1 flex items-baseline justify-between gap-2">
                  <span className="truncate text-[13px] font-semibold text-mc-navy">{MARCA_BY_ID[c.clave as keyof typeof MARCA_BY_ID]?.label ?? c.nombre}</span>
                  <span className="shrink-0 font-mono text-[11px] text-mc-grey">{ars(c.coste)}</span>
                </div>
                <BarraConsumo valor={consumoMes(c.coste, c.presDia, diasMes)} semaforo={semaforo(c.coste, c.presDia, dias)} marca={r.esperado} />
              </div>
            ))}
          </div>
        </Tarjeta>
        <div className="mt-3 flex flex-wrap gap-2 text-[13px]">
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-red-50 px-3 py-1.5 text-red-800 ring-1 ring-red-200">
            <AlertTriangle size={14} /> <b>{r.sobre.length}</b> {r.sobre.length === 1 ? 'campaña gasta' : 'campañas gastan'} más de un 5% por encima de su presupuesto
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-red-50 px-3 py-1.5 text-red-800 ring-1 ring-red-200">
            <CircleSlash size={14} /> <b>{r.sinGasto.length}</b> {r.sinGasto.length === 1 ? 'campaña activa no gasta' : 'campañas activas no gastan'} nada
          </span>
        </div>
      </section>

      <section>
        <SeccionTitulo meta="Search · Google Ads">Embudo de conversión — impresión → clic → conversión</SeccionTitulo>
        <Tarjeta className="p-5">
          <Embudo impresiones={r.impresiones} clics={r.clics} conv={r.conv} coste={r.gasto} />
        </Tarjeta>
      </section>

      <PanelOscuro titulo="Rotación de inversión" icono={<Repeat size={15} />} meta="mover presupuesto sin subir el total">
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
          <div>
            <h3 className="mb-1 flex items-center gap-1.5 text-sm">
              <ArrowUpRight size={16} className="text-mc-red" /> Topeadas: piden más presupuesto
            </h3>
            <p className="mb-2 text-xs text-mc-grey">Gastan el {Math.round(UMBRAL_TOPE * 100)}% o más de lo asignado por día. Si convierten o tienen buena relevancia, son las candidatas a recibir inversión.</p>
            <Lista filas={r.topeadas} vacio="Ninguna campaña está limitada por presupuesto." tipo="tope" />
          </div>
          <div className="lg:border-l lg:border-mc-tint2 lg:pl-5">
            <h3 className="mb-1 flex items-center gap-1.5 text-sm">
              <ArrowDownRight size={16} className="text-mc-blue" /> Con presupuesto ocioso: de dónde sacarlo
            </h3>
            <p className="mb-2 text-xs text-mc-grey">Gastan menos del {Math.round(UMBRAL_OCIOSO * 100)}% de lo asignado. Ese sobrante se puede mover a las topeadas.</p>
            <Lista filas={r.ociosas} vacio="No hay presupuesto ocioso." tipo="ocio" />
          </div>
        </div>
      </PanelOscuro>
    </div>
  );
}
