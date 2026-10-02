/**
 * Vista «Día a día» del presupuesto: cada día contra el presupuesto diario.
 *  - Calendario del mes: un casillero por día con el total (gasto ÷ presupuesto de las campañas activas).
 *  - Detalle del día elegido (por defecto, el último con datos): cada campaña con su barra de uso.
 *  - Grilla campaña × día: el patrón de cada campaña a lo largo del mes.
 * Respeta los filtros de cliente, país y búsqueda de la vista de presupuesto.
 */
import { useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { MARCA_BY_ID, MARCAS } from '@/constants/estados';
import { Tarjeta, Vacio } from '@/components/shared/Ui';
import type { MetricaDia } from '@/services/metricas';
import { ars, campanaCorta, mesCorto } from '@/utils/formato';
import { diaSemana, estadoDia, fechasDelMes, presupuestoActivo, totalDia, type CampanaGasto, type EstadoDia, type Semaforo } from '@/utils/presupuesto';
import { BarraConsumo } from './Semaforo';

const CELDA: Record<EstadoDia, string> = {
  sobre: 'bg-red-500',
  sin: 'bg-red-200',
  ok: 'bg-emerald-500',
  gris: 'bg-mc-tint2',
};
const CASILLERO: Record<EstadoDia, string> = {
  sobre: 'bg-red-50 text-red-800 ring-red-300',
  sin: 'bg-red-50/60 text-red-700 ring-red-200',
  ok: 'bg-emerald-50 text-emerald-800 ring-emerald-200',
  gris: 'bg-mc-tint2 text-mc-grey ring-mc-hair',
};
const ETIQUETA: Record<EstadoDia, string> = { sobre: 'superó', sin: 'sin gasto', ok: 'dentro', gris: 'sin presupuesto' };
const A_SEMAFORO: Record<EstadoDia, Semaforo> = { sobre: 'rojo', sin: 'rojo', ok: 'verde', gris: 'gris' };
const ORDEN: Record<EstadoDia, number> = { sobre: 0, sin: 1, ok: 2, gris: 3 };
const SEMANA = ['L', 'M', 'M', 'J', 'V', 'S', 'D'];

const diaCorto = (f: string) => `${Number(f.slice(8, 10))} ${mesCorto(f.slice(0, 7)).split(' ')[0]}`;

export default function VistaDiaria({ campanas, dias }: { campanas: CampanaGasto[]; dias: MetricaDia[] }) {
  const meses = useMemo(() => [...new Set(dias.map((d) => d.fecha.slice(0, 7)))].sort(), [dias]);
  const [mesElegido, setMes] = useState('');
  const mes = meses.includes(mesElegido) ? mesElegido : (meses[meses.length - 1] ?? '');
  const hasta = useMemo(() => dias.filter((d) => d.fecha.startsWith(mes)).reduce((m, d) => (d.fecha > m ? d.fecha : m), ''), [dias, mes]);
  const fechas = useMemo(() => (mes ? fechasDelMes(mes, hasta || null) : []), [mes, hasta]);
  const [elegido, setElegido] = useState('');
  const dia = fechas.includes(elegido) ? elegido : (fechas[fechas.length - 1] ?? '');

  const gasto = useMemo(() => new Map(dias.map((d) => [`${d.campanaId}|${d.fecha}`, d.coste])), [dias]);
  // filas: campañas activas o con gasto en el mes, agrupadas por cliente
  const filas = useMemo(() => {
    const conGasto = new Set(dias.filter((d) => d.fecha.startsWith(mes) && d.coste > 0).map((d) => d.campanaId));
    return campanas
      .filter((c) => presupuestoActivo(c) || conGasto.has(c.id))
      .sort(
        (a, b) =>
          MARCAS.findIndex((m) => m.id === a.marca) - MARCAS.findIndex((m) => m.id === b.marca) ||
          a.unidad.localeCompare(b.unidad) ||
          a.nombre.localeCompare(b.nombre),
      );
  }, [campanas, dias, mes]);
  const totales = useMemo(() => fechas.map((f) => totalDia(f, filas, gasto)), [fechas, filas, gasto]);
  const totalElegido = totales.find((t) => t.fecha === dia);
  const detalle = useMemo(
    () =>
      filas
        .map((c) => {
          const g = gasto.get(`${c.id}|${dia}`) ?? 0;
          const p = presupuestoActivo(c);
          return { c, g, p, estado: estadoDia(g, p) };
        })
        .sort((a, b) => ORDEN[a.estado] - ORDEN[b.estado] || (b.p ? b.g / b.p : 0) - (a.p ? a.g / a.p : 0)),
    [filas, gasto, dia],
  );

  if (!meses.length) return <Vacio>Todavía no hay gasto por día cargado. Corré ads_diario.py y scripts/publicar.py.</Vacio>;
  const i = meses.indexOf(mes);
  const huecos = fechas.length ? diaSemana(fechas[0]) : 0;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[400px_minmax(0,1fr)]">
        {/* calendario del mes */}
        <Tarjeta className="p-4">
          <div className="mb-3 flex items-center justify-between">
            <button
              type="button"
              aria-label="Mes anterior"
              disabled={i <= 0}
              onClick={() => setMes(meses[i - 1])}
              className="rounded-md p-1 text-mc-navy hover:bg-mc-tint disabled:opacity-30"
            >
              <ChevronLeft size={18} />
            </button>
            <span className="text-sm font-bold capitalize text-mc-navy">{mesCorto(mes)}</span>
            <button
              type="button"
              aria-label="Mes siguiente"
              disabled={i >= meses.length - 1}
              onClick={() => setMes(meses[i + 1])}
              className="rounded-md p-1 text-mc-navy hover:bg-mc-tint disabled:opacity-30"
            >
              <ChevronRight size={18} />
            </button>
          </div>
          <div className="grid grid-cols-7 gap-1.5 text-center">
            {SEMANA.map((s, k) => (
              <span key={k} className="text-[10px] font-semibold uppercase text-mc-grey">
                {s}
              </span>
            ))}
            {Array.from({ length: huecos }, (_, k) => (
              <span key={`h${k}`} />
            ))}
            {totales.map((t) => {
              const uso = t.presDia ? t.coste / t.presDia : null;
              return (
                <button
                  key={t.fecha}
                  type="button"
                  onClick={() => setElegido(t.fecha)}
                  title={`${diaCorto(t.fecha)}: ${ars(t.coste)} de ${t.presDia ? ars(t.presDia) : '—'} · ${t.sobre} superaron, ${t.sin} sin gasto`}
                  className={`flex h-12 flex-col items-start justify-between rounded-lg px-1.5 py-1 text-left ring-1 transition hover:-translate-y-0.5 ${CASILLERO[t.estado]} ${t.fecha === dia ? 'outline outline-2 outline-offset-1 outline-mc-navy' : ''}`}
                >
                  <span className="flex w-full items-center justify-between text-[10px] font-semibold">
                    <span className="opacity-80">{Number(t.fecha.slice(8, 10))}</span>
                    {t.sobre > 0 && (
                      <span className="rounded bg-red-500 px-1 text-[9px] leading-[14px] text-white" title={`${t.sobre} campañas superaron su presupuesto`}>
                        ▲{t.sobre}
                      </span>
                    )}
                  </span>
                  <span className="font-mono text-[11px] font-bold">{uso === null ? '—' : `${Math.round(uso * 100)}%`}</span>
                </button>
              );
            })}
          </div>
          <p className="mt-3 text-[11px] text-mc-grey">
            Cada casillero: gasto del día sobre el presupuesto diario de las campañas activas. Clic para ver el detalle.
          </p>
        </Tarjeta>

        {/* detalle del día */}
        <Tarjeta className="flex flex-col p-4">
          <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2 border-b border-mc-tint2 pb-3">
            <div>
              <div className="text-[10px] font-bold uppercase tracking-[0.14em] text-mc-grey">Día elegido</div>
              <div className="text-lg font-bold capitalize text-mc-navy">{diaCorto(dia)}</div>
            </div>
            {totalElegido && (
              <div className="flex flex-wrap items-center gap-2 text-[12px]">
                <span className="font-mono text-mc-navy">
                  {ars(totalElegido.coste)} de {totalElegido.presDia ? ars(totalElegido.presDia) : '—'}
                </span>
                <span className="rounded-full bg-red-50 px-2 py-0.5 font-semibold text-red-700 ring-1 ring-red-200">{totalElegido.sobre} superaron</span>
                <span className="rounded-full bg-red-50/60 px-2 py-0.5 font-semibold text-red-700 ring-1 ring-red-100">{totalElegido.sin} sin gasto</span>
                <span className="rounded-full bg-emerald-50 px-2 py-0.5 font-semibold text-emerald-700 ring-1 ring-emerald-200">{totalElegido.ok} dentro</span>
              </div>
            )}
          </div>
          <ul className="max-h-[248px] flex-1 space-y-1 overflow-y-auto pr-1">
            {detalle.map(({ c, g, p, estado }) => (
              <li
                key={c.id}
                className="grid grid-cols-[minmax(0,1fr)_92px_minmax(110px,170px)] items-center gap-3 rounded-md px-1.5 py-1 text-[12.5px] hover:bg-mc-tint"
              >
                <span className="truncate text-mc-navy" title={c.nombre}>
                  <span className="mr-1.5 rounded bg-mc-navy px-1 py-0.5 text-[10px] font-semibold text-white">{c.marca}</span>
                  {campanaCorta(c.nombre)}
                </span>
                <span className="text-right font-mono text-[11.5px] text-mc-ink">
                  {ars(g)}
                  {p ? <span className="block text-[10px] text-mc-grey">de {ars(p)}</span> : null}
                </span>
                {p ? <BarraConsumo valor={g / p} semaforo={A_SEMAFORO[estado]} /> : <span className="text-[11px] text-mc-grey">sin presupuesto activo</span>}
              </li>
            ))}
          </ul>
        </Tarjeta>
      </div>

      {/* grilla campaña × día */}
      <Tarjeta className="overflow-x-auto p-4">
        <div className="mb-2 flex items-baseline justify-between">
          <h3 className="text-sm font-bold text-mc-navy">Cada campaña, día por día</h3>
          <span className="text-[11px] text-mc-grey">pasá el mouse por un casillero para ver el gasto; clic para elegir el día</span>
        </div>
        <table className="border-separate border-spacing-[3px] text-[11px]">
          <thead>
            <tr>
              <th className="sticky left-0 z-10 min-w-[230px] bg-white" />
              {fechas.map((f) => (
                <th
                  key={f}
                  className={`w-4 cursor-pointer text-center font-mono font-normal ${f === dia ? 'font-bold text-mc-navy' : 'text-mc-grey'}`}
                  onClick={() => setElegido(f)}
                >
                  {Number(f.slice(8, 10))}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filas.map((c, k) => {
              const nuevoCliente = k === 0 || filas[k - 1].marca !== c.marca;
              const p = presupuestoActivo(c);
              return (
                <tr key={c.id}>
                  <td
                    className={`sticky left-0 z-10 max-w-[230px] truncate bg-white pr-2 text-mc-navy ${nuevoCliente && k ? 'border-t-2 border-mc-hair pt-1' : ''}`}
                    title={c.nombre}
                  >
                    {nuevoCliente && (
                      <span className="mb-0.5 block text-[9.5px] font-bold uppercase tracking-[0.12em] text-mc-grey">
                        {MARCA_BY_ID[c.marca as keyof typeof MARCA_BY_ID]?.label ?? c.marca}
                      </span>
                    )}
                    {campanaCorta(c.nombre)}
                  </td>
                  {fechas.map((f) => {
                    const g = gasto.get(`${c.id}|${f}`) ?? 0;
                    const e = estadoDia(g, p);
                    return (
                      <td key={f} className={`${nuevoCliente && k ? 'border-t-2 border-mc-hair pt-1' : ''} align-bottom`}>
                        <button
                          type="button"
                          onClick={() => setElegido(f)}
                          title={`${campanaCorta(c.nombre)} · ${diaCorto(f)}: ${ars(g)}${p ? ` de ${ars(p)} (${Math.round((g / p) * 100)}%)` : ' · sin presupuesto activo'} · ${ETIQUETA[e]}`}
                          className={`block h-4 w-4 rounded-[3px] ${CELDA[e]} ${f === dia ? 'ring-2 ring-mc-navy ring-offset-1' : ''}`}
                        />
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </Tarjeta>
    </div>
  );
}
