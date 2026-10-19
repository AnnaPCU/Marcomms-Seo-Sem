/**
 * Vista «Histórico» del presupuesto: cómo evolucionó el gasto de Google Ads mes a mes.
 *  - Barras del gasto por mes, apiladas por cliente.
 *  - Tabla mes a mes: gasto, variación, clics, CPC, CTR, conversiones y campañas con actividad.
 *  - Matriz cliente → país → campaña × mes, con el indicador que se elija.
 * Respeta los filtros de cliente y país de la vista de presupuesto. Todo en pesos: la cuenta anterior
 * (feb–jul 2026) facturaba en euros y se convirtió con el tipo de cambio oficial del BCRA, promedio de cada mes.
 */
import { useMemo, useState } from 'react';
import { ChevronRight } from 'lucide-react';
import { MARCA_BY_ID, MARCAS } from '@/constants/estados';
import { SeccionTitulo, Tarjeta, Vacio } from '@/components/shared/Ui';
import type { MetricaMes } from '@/services/metricas';
import { ars, campanaCorta, compacto, entero, fecha, mesCorto, pct, signo } from '@/utils/formato';
import { costoConv, cpc, ctr, matriz, serieMensual, variacion, type CampanaRef, type FilaMatriz, type Totales } from '@/utils/historico';

// Colores por cliente en la paleta MarComms (nunca los de Control Union ni Peterson).
const COLOR_MARCA: Record<string, string> = { CU: 'bg-mc-navy', PCU: 'bg-mc-blue', PS: 'bg-mc-gold' };

type Indicador = 'coste' | 'clics' | 'cpc' | 'conv';
const INDICADORES: { id: Indicador; label: string }[] = [
  { id: 'coste', label: 'Gasto' },
  { id: 'clics', label: 'Clics' },
  { id: 'cpc', label: 'CPC' },
  { id: 'conv', label: 'Conversiones' },
];

function valor(t: Totales | undefined, ind: Indicador): number | null {
  if (!t) return null;
  if (ind === 'coste') return t.coste;
  if (ind === 'clics') return t.clics;
  if (ind === 'conv') return t.conv;
  return cpc(t);
}

function texto(v: number | null, ind: Indicador): string {
  if (v === null) return '';
  if (ind === 'coste' || ind === 'cpc') return compacto(v);
  return entero(v);
}

/** Verde si mejora y rojo si empeora; `neutra` para el gasto, que subir o bajar no es bueno ni malo en sí. */
function Variacion({ v, neutra }: { v: number | null; neutra?: boolean }) {
  if (v === null) return <span className="text-mc-grey">—</span>;
  const color = Math.abs(v) < 0.005 ? 'text-mc-grey' : neutra ? 'text-mc-ink' : v > 0 ? 'text-emerald-700' : 'text-red-700';
  return <span className={color}>{signo(v)}</span>;
}

function FilaHeat({
  f,
  meses,
  ind,
  abiertos,
  alternar,
}: {
  f: FilaMatriz;
  meses: string[];
  ind: Indicador;
  abiertos: Set<string>;
  alternar: (k: string) => void;
}) {
  const abierto = abiertos.has(f.clave);
  const valores = meses.map((m) => valor(f.porMes.get(m), ind));
  const max = Math.max(...valores.map((v) => v ?? 0), 0);
  const nombre = f.nivel === 1 ? (MARCA_BY_ID[f.clave as keyof typeof MARCA_BY_ID]?.label ?? f.nombre) : f.nivel === 3 ? campanaCorta(f.nombre) : f.nombre;
  const fondo = f.nivel === 1 ? 'bg-mc-tint2 font-bold' : f.nivel === 2 ? 'bg-mc-tint font-semibold' : 'bg-white';
  return (
    <>
      <tr className={`border-t border-mc-tint2 ${fondo} ${f.hijos.length ? 'cursor-pointer hover:bg-mc-tint' : ''}`} onClick={() => f.hijos.length && alternar(f.clave)}>
        <td className={`sticky left-0 z-10 max-w-[280px] truncate py-1.5 pr-3 text-mc-navy ${fondo} ${['', 'pl-3', 'pl-7', 'pl-11'][f.nivel]}`} title={f.nombre}>
          <span className="inline-flex items-center gap-1">
            {f.hijos.length ? <ChevronRight size={13} className={`shrink-0 text-mc-grey transition ${abierto ? 'rotate-90' : ''}`} /> : null}
            <span className="truncate">{nombre}</span>
            {f.cuenta === 'anterior' && <span className="shrink-0 rounded bg-mc-tint2 px-1 text-[10px] font-normal text-mc-grey">cuenta anterior</span>}
          </span>
        </td>
        {valores.map((v, i) => (
          <td key={meses[i]} className="px-1 py-1 text-right font-mono text-[12px]">
            {v === null || v === 0 ? (
              <span className="text-mc-hair">·</span>
            ) : (
              <span
                className="block rounded px-1.5 py-0.5 text-mc-navy"
                style={{ backgroundColor: `rgba(0, 156, 235, ${max ? 0.08 + 0.42 * (v / max) : 0})` }}
                title={`${mesCorto(meses[i])}: ${ind === 'coste' || ind === 'cpc' ? ars(v) : entero(v)}`}
              >
                {texto(v, ind)}
              </span>
            )}
          </td>
        ))}
        <td className="px-2 py-1 text-right font-mono text-[12px] font-semibold text-mc-navy">{texto(valor(f.total, ind), ind)}</td>
      </tr>
      {abierto && f.hijos.map((h) => <FilaHeat key={h.clave} f={h} meses={meses} ind={ind} abiertos={abiertos} alternar={alternar} />)}
    </>
  );
}

export default function VistaHistorica({ campanas, metricas, mesEnCurso }: { campanas: CampanaRef[]; metricas: MetricaMes[]; mesEnCurso: string }) {
  const [ind, setInd] = useState<Indicador>('coste');
  const [abiertos, setAbiertos] = useState<Set<string>>(() => new Set(MARCAS.map((m) => m.id)));
  const serie = useMemo(() => serieMensual(campanas, metricas), [campanas, metricas]);
  const filas = useMemo(
    () =>
      matriz(
        campanas,
        metricas,
        MARCAS.map((m) => m.id),
      ),
    [campanas, metricas],
  );
  const meses = serie.map((s) => s.mes);
  const maxCoste = Math.max(...serie.map((s) => s.coste), 1);
  const tipos = useMemo(() => {
    const t = new Map<string, number>();
    metricas.forEach((m) => m.tipoCambio && m.monedaOriginal && t.set(m.mes, m.tipoCambio));
    return [...t.entries()].sort();
  }, [metricas]);
  const hastaEnCurso = metricas.filter((m) => m.mes === mesEnCurso).map((m) => m.hasta ?? '').sort().pop();

  const alternar = (k: string) =>
    setAbiertos((prev) => {
      const s = new Set(prev);
      if (s.has(k)) s.delete(k);
      else s.add(k);
      return s;
    });

  if (!serie.length) return <Vacio>No hay gasto histórico para este filtro.</Vacio>;
  const marcas = MARCAS.filter((m) => serie.some((s) => s.porMarca[m.id]));

  return (
    <div className="space-y-6">
      <Tarjeta className="p-4">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <span className="text-[11px] font-bold uppercase tracking-[0.14em] text-mc-grey">Gasto por mes · en pesos</span>
          <span className="flex flex-wrap gap-3 text-xs text-mc-grey">
            {marcas.map((m) => (
              <span key={m.id} className="flex items-center gap-1.5">
                <span className={`inline-block h-2.5 w-2.5 rounded-sm ${COLOR_MARCA[m.id]}`} />
                {m.label}
              </span>
            ))}
          </span>
        </div>
        <div className="flex h-44 items-end gap-2 overflow-x-auto pb-1">
          {serie.map((s) => {
            const parcial = s.mes === mesEnCurso;
            return (
              <div key={s.mes} className="flex min-w-[52px] flex-1 flex-col items-center justify-end gap-1" title={`${mesCorto(s.mes)}: ${ars(s.coste)} · ${entero(s.clics)} clics`}>
                <span className="font-mono text-[11px] font-semibold text-mc-navy">{s.coste ? compacto(s.coste) : '—'}</span>
                <div className={`flex w-full max-w-[56px] flex-col-reverse overflow-hidden rounded-t ${parcial ? 'opacity-60' : ''}`} style={{ height: `${(s.coste / maxCoste) * 112}px` }}>
                  {marcas.map((m) => (
                    <div key={m.id} className={COLOR_MARCA[m.id]} style={{ height: `${s.coste ? ((s.porMarca[m.id] ?? 0) / s.coste) * 100 : 0}%` }} />
                  ))}
                </div>
                <span className="text-[11px] text-mc-ink">
                  {mesCorto(s.mes).replace(' de ', ' ')}
                  {parcial && <span className="text-mc-grey">*</span>}
                </span>
              </div>
            );
          })}
        </div>
      </Tarjeta>

      <section>
        <SeccionTitulo meta="del más reciente al más viejo · variación contra el mes anterior">Mes a mes</SeccionTitulo>
        <Tarjeta className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-[13px]">
            <thead>
              <tr className="text-left text-[10px] uppercase tracking-[0.12em] text-mc-grey">
                <th className="px-4 py-2 font-semibold">Mes</th>
                <th className="px-2 py-2 text-right font-semibold">Gasto</th>
                <th className="px-2 py-2 text-right font-semibold">vs. ant.</th>
                <th className="px-2 py-2 text-right font-semibold">Clics</th>
                <th className="px-2 py-2 text-right font-semibold">vs. ant.</th>
                <th className="px-2 py-2 text-right font-semibold">CPC</th>
                <th className="px-2 py-2 text-right font-semibold">CTR</th>
                <th className="px-2 py-2 text-right font-semibold">Conv.</th>
                <th className="px-2 py-2 text-right font-semibold">Costo / conv.</th>
                <th className="px-4 py-2 text-right font-semibold">Campañas</th>
              </tr>
            </thead>
            <tbody>
              {[...serie].reverse().map((s, i, arr) => {
                const ant = arr[i + 1];
                // el mes en curso se compara por día para no castigarlo por estar incompleto
                const escala = s.mes === mesEnCurso && s.dias < s.diasMes ? s.diasMes / s.dias : 1;
                return (
                  <tr key={s.mes} className="border-t border-mc-tint2">
                    <td className="px-4 py-2 font-semibold text-mc-navy">
                      {mesCorto(s.mes)}
                      {s.mes === mesEnCurso && <span className="ml-1 text-[11px] font-normal text-mc-grey">en curso{hastaEnCurso ? `, al ${fecha(hastaEnCurso)}` : ''}</span>}
                      {s.costeEur > 0 && <span className="ml-1 text-[11px] font-normal text-mc-grey">· {pct(s.costeEur, s.coste)} cuenta anterior</span>}
                    </td>
                    <td className="px-2 py-2 text-right font-mono text-mc-navy">{ars(s.coste)}</td>
                    <td className="px-2 py-2 text-right font-mono text-xs">
                      <Variacion neutra v={ant ? variacion(s.coste * escala, ant.coste) : null} />
                    </td>
                    <td className="px-2 py-2 text-right font-mono">{entero(s.clics)}</td>
                    <td className="px-2 py-2 text-right font-mono text-xs">
                      <Variacion v={ant ? variacion(s.clics * escala, ant.clics) : null} />
                    </td>
                    <td className="px-2 py-2 text-right font-mono">{ars(cpc(s))}</td>
                    <td className="px-2 py-2 text-right font-mono">{ctr(s) === null ? '—' : pct(s.clics, s.impresiones, 1)}</td>
                    <td className={`px-2 py-2 text-right font-mono ${s.conv ? 'font-semibold text-mc-blue' : 'text-mc-grey'}`}>{Math.round(s.conv)}</td>
                    <td className="px-2 py-2 text-right font-mono">{ars(costoConv(s))}</td>
                    <td className="px-4 py-2 text-right font-mono">{s.campanas}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Tarjeta>
      </section>

      <section>
        <SeccionTitulo meta="clic en un cliente o país para abrirlo">Por cliente, país y campaña</SeccionTitulo>
        <div className="mb-3 inline-flex overflow-hidden rounded-lg border border-mc-hair bg-white text-sm">
          {INDICADORES.map((x) => (
            <button
              key={x.id}
              type="button"
              onClick={() => setInd(x.id)}
              className={`px-3 py-1.5 font-medium transition ${ind === x.id ? 'bg-mc-navy text-white' : 'text-mc-ink hover:bg-mc-tint'}`}
            >
              {x.label}
            </button>
          ))}
        </div>
        <Tarjeta className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-[13px]">
            <thead>
              <tr className="text-[10px] uppercase tracking-[0.12em] text-mc-grey">
                <th className="sticky left-0 z-10 bg-white px-3 py-2 text-left font-semibold">Nivel</th>
                {meses.map((m) => (
                  <th key={m} className="px-1 py-2 text-right font-semibold">
                    {mesCorto(m).replace(' de ', ' ')}
                    {m === mesEnCurso && '*'}
                  </th>
                ))}
                <th className="px-2 py-2 text-right font-semibold">{ind === 'cpc' ? 'Prom.' : 'Total'}</th>
              </tr>
            </thead>
            <tbody>
              {filas.map((f) => (
                <FilaHeat key={f.clave} f={f} meses={meses} ind={ind} abiertos={abiertos} alternar={alternar} />
              ))}
            </tbody>
          </table>
        </Tarjeta>
      </section>

      <p className="text-xs leading-relaxed text-mc-grey">
        * Mes en curso{hastaEnCurso ? `, con datos al ${fecha(hastaEnCurso)}` : ''}: en la tabla, la variación se calcula sobre el ritmo diario para no
        compararlo incompleto. Todo en pesos.
        {tipos.length > 0 && (
          <>
            {' '}
            De feb a jul 2026 las campañas estaban en la cuenta anterior («Peterson Technologies»), que factura en euros: se convirtieron con el tipo de cambio
            oficial del BCRA, promedio de cada mes ({tipos.map(([m, t]) => `${mesCorto(m).replace(' de ', ' ')} ${Math.round(t).toLocaleString('es-AR')}`).join(' · ')}).
            En julio conviven las dos cuentas; las campañas de la anterior llevan la marca «cuenta anterior».
          </>
        )}
      </p>
    </div>
  );
}
