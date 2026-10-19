/**
 * Sitios · vista «Histórico»: cómo evolucionó cada sitio mes a mes según GA4 (desde dic 2025, cuando empiezan los datos).
 *  - Barras de visitas reales (con interacción) por mes, apiladas por canal.
 *  - Tabla mes a mes con la variación contra el mes anterior.
 *  - Matriz sitio × mes con el indicador que se elija.
 */
import { useMemo, useState } from 'react';
import type { Ga4SitioMes } from '@/services/ga4';
import { ChipMarca, SeccionTitulo, Tarjeta, Vacio } from '@/components/shared/Ui';
import { compacto, entero, fecha, mesCorto, pct, signo } from '@/utils/formato';
import { canal, CANALES, serieSitios, tasa } from '@/utils/ga4';
import { variacion } from '@/utils/historico';

type Indicador = 'interaccion' | 'sesiones' | 'contactos' | 'organico' | 'pago';
const INDICADORES: { id: Indicador; label: string; pct?: boolean }[] = [
  { id: 'interaccion', label: 'Visitas reales' },
  { id: 'sesiones', label: 'Sesiones' },
  { id: 'contactos', label: 'Contactos' },
  { id: 'organico', label: '% orgánico', pct: true },
  { id: 'pago', label: 'Visitas pagas' },
];
const TRAMOS = [...CANALES, { id: 'otros', label: 'Otros', color: 'bg-mc-hair' }];

function valor(s: Ga4SitioMes | undefined, ind: Indicador): number | null {
  if (!s) return null;
  const d = s.datos;
  if (ind === 'interaccion') return d.interaccion;
  if (ind === 'sesiones') return d.sesiones;
  if (ind === 'contactos') return d.contactos_total;
  if (ind === 'pago') return canal(d, 'Paid Search').sesiones;
  return d.sesiones ? canal(d, 'Organic Search').sesiones / d.sesiones : null;
}

function Variacion({ v }: { v: number | null }) {
  if (v === null) return <span className="text-mc-grey">—</span>;
  return <span className={Math.abs(v) < 0.005 ? 'text-mc-grey' : v > 0 ? 'text-emerald-700' : 'text-red-700'}>{signo(v)}</span>;
}

export default function VistaSitiosHistorica({ datos, mesEnCurso }: { datos: Ga4SitioMes[]; mesEnCurso: string }) {
  const [ind, setInd] = useState<Indicador>('interaccion');
  const serie = useMemo(() => serieSitios(datos), [datos]);
  const meses = serie.map((s) => s.mes);
  const sitios = useMemo(() => {
    const m = new Map<string, { sitio: string; nombre: string; marca: Ga4SitioMes['marca']; porMes: Map<string, Ga4SitioMes>; total: number }>();
    for (const s of datos) {
      let x = m.get(s.sitio);
      if (!x) m.set(s.sitio, (x = { sitio: s.sitio, nombre: s.nombre, marca: s.marca, porMes: new Map(), total: 0 }));
      x.porMes.set(s.mes, s);
      x.total += s.datos.interaccion;
    }
    return [...m.values()].sort((a, b) => b.total - a.total);
  }, [datos]);
  const enCurso = serie.find((s) => s.mes === mesEnCurso);
  const hastaEnCurso = datos.find((s) => s.mes === mesEnCurso)?.hasta;
  const def = INDICADORES.find((x) => x.id === ind)!;

  if (!serie.length) return <Vacio>No hay datos de GA4 para este filtro.</Vacio>;
  const max = Math.max(...serie.map((s) => s.interaccion), 1);

  return (
    <div className="space-y-6">
      <Tarjeta className="p-4">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <span className="text-[11px] font-bold uppercase tracking-[0.14em] text-mc-grey">Visitas reales por mes, según de dónde llegan</span>
          <span className="flex flex-wrap gap-3 text-xs text-mc-grey">
            {TRAMOS.map((c) => (
              <span key={c.id} className="flex items-center gap-1.5">
                <span className={`inline-block h-2.5 w-2.5 rounded-sm ${c.color}`} />
                {c.label}
              </span>
            ))}
          </span>
        </div>
        <div className="flex h-44 items-end gap-2 overflow-x-auto pb-1">
          {serie.map((s) => (
            <div key={s.mes} className="flex min-w-[48px] flex-1 flex-col items-center justify-end gap-1" title={`${mesCorto(s.mes)}: ${entero(s.interaccion)} visitas reales`}>
              <span className="font-mono text-[11px] font-semibold text-mc-navy">{compacto(s.interaccion)}</span>
              <div className={`flex w-full max-w-[52px] flex-col-reverse overflow-hidden rounded-t ${s.mes === mesEnCurso ? 'opacity-60' : ''}`} style={{ height: `${(s.interaccion / max) * 112}px` }}>
                {TRAMOS.map((c) => (
                  <div key={c.id} className={c.color} style={{ height: `${tasa(s.canales[c.id] ?? 0, s.interaccion) * 100}%` }} />
                ))}
              </div>
              <span className="text-[11px] text-mc-ink">
                {mesCorto(s.mes)}
                {s.mes === mesEnCurso && <span className="text-mc-grey">*</span>}
              </span>
            </div>
          ))}
        </div>
      </Tarjeta>

      <section>
        <SeccionTitulo meta="del más reciente al más viejo · variación contra el mes anterior">Mes a mes</SeccionTitulo>
        <Tarjeta className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-[13px]">
            <thead>
              <tr className="text-left text-[10px] uppercase tracking-[0.12em] text-mc-grey">
                <th className="px-4 py-2 font-semibold">Mes</th>
                <th className="px-2 py-2 text-right font-semibold">Visitas reales</th>
                <th className="px-2 py-2 text-right font-semibold">vs. ant.</th>
                <th className="px-2 py-2 text-right font-semibold">Sesiones</th>
                <th className="px-2 py-2 text-right font-semibold">Con interacción</th>
                <th className="px-2 py-2 text-right font-semibold">Orgánico</th>
                <th className="px-2 py-2 text-right font-semibold">Contactos</th>
                <th className="px-4 py-2 text-right font-semibold">vs. ant.</th>
              </tr>
            </thead>
            <tbody>
              {[...serie].reverse().map((s, i, arr) => {
                const ant = arr[i + 1];
                const escala = s.dias < s.diasMes ? s.diasMes / s.dias : 1; // el mes en curso, por ritmo diario
                return (
                  <tr key={s.mes} className="border-t border-mc-tint2">
                    <td className="px-4 py-2 font-semibold text-mc-navy">
                      {mesCorto(s.mes)}
                      {s.dias < s.diasMes && <span className="ml-1 text-[11px] font-normal text-mc-grey">{s.dias} días</span>}
                    </td>
                    <td className="px-2 py-2 text-right font-mono text-mc-navy">{entero(s.interaccion)}</td>
                    <td className="px-2 py-2 text-right font-mono text-xs">
                      <Variacion v={ant ? variacion(s.interaccion * escala, ant.interaccion) : null} />
                    </td>
                    <td className="px-2 py-2 text-right font-mono">{entero(s.sesiones)}</td>
                    <td className="px-2 py-2 text-right font-mono">{pct(s.interaccion, s.sesiones)}</td>
                    <td className="px-2 py-2 text-right font-mono">{pct(s.canales['Organic Search'] ?? 0, s.interaccion)}</td>
                    <td className="px-2 py-2 text-right font-mono font-semibold text-mc-navy">{entero(s.contactos)}</td>
                    <td className="px-4 py-2 text-right font-mono text-xs">
                      <Variacion v={ant ? variacion(s.contactos * escala, ant.contactos) : null} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Tarjeta>
      </section>

      <section>
        <SeccionTitulo meta="cada fila, de su mes más bajo (claro) al más alto (oscuro)">Por sitio</SeccionTitulo>
        <div className="mb-3 inline-flex flex-wrap overflow-hidden rounded-lg border border-mc-hair bg-white text-sm">
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
                <th className="sticky left-0 z-10 bg-white px-3 py-2 text-left font-semibold">Sitio</th>
                {meses.map((m) => (
                  <th key={m} className="px-1 py-2 text-right font-semibold">
                    {mesCorto(m)}
                    {m === mesEnCurso && '*'}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sitios.map((x) => {
                const valores = meses.map((m) => valor(x.porMes.get(m), ind));
                const tope = Math.max(...valores.map((v) => v ?? 0), 0);
                return (
                  <tr key={x.sitio} className="border-t border-mc-tint2">
                    <td className="sticky left-0 z-10 max-w-[230px] bg-white px-3 py-1.5" title={x.sitio}>
                      <span className="flex items-center gap-1.5 font-semibold text-mc-navy">
                        <ChipMarca marca={x.marca} />
                        <span className="truncate">{x.nombre.replace(/^(Control Union|Peterson Solutions)\s*/, '')}</span>
                      </span>
                    </td>
                    {valores.map((v, i) => (
                      <td key={meses[i]} className="px-1 py-1 text-right font-mono text-[12px]">
                        {v === null ? (
                          <span className="text-mc-hair">·</span>
                        ) : (
                          <span className="block rounded px-1.5 py-0.5 text-mc-navy" style={{ backgroundColor: `rgba(0, 156, 235, ${tope ? 0.06 + 0.44 * (v / tope) : 0})` }}>
                            {def.pct ? `${Math.round(v * 100)}%` : entero(v)}
                          </span>
                        )}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Tarjeta>
      </section>

      <p className="text-xs leading-relaxed text-mc-grey">
        {enCurso && `* Mes en curso, con ${enCurso.dias} días${hastaEnCurso ? ` (al ${fecha(hastaEnCurso)})` : ''}: la variación se calcula sobre el ritmo diario. `}
        Las propiedades de GA4 tienen datos desde fines de nov 2025. Los contactos cuentan formularios del sitio y clics a un email comercial; los formularios
        de HubSpot no llegan a GA4. Dic 2025 y, desde mayo 2026, todos los meses traen mucho tráfico directo sin interacción (bots) en casi todos los sitios: por
        eso conviene mirar las visitas reales y no las sesiones.
      </p>
    </div>
  );
}
