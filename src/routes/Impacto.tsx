/**
 * Impacto: qué pasó después de cada optimización SEM «hecha». Se elige un país y se recorren de a una.
 * Solo se muestran las que ya juntaron 14 días de datos después del cambio; mientras ninguna llega, «Próximamente».
 * El cálculo (cruce con el historial de cambios de Ads y antes / después) vive en utils/impacto.ts.
 */
import { useEffect, useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight, Hourglass } from 'lucide-react';
import { MARCAS } from '@/constants/estados';
import { listarEventosDe, type Evento } from '@/services/recomendaciones';
import { useCambiosAds, useCampanas, useMetricasDia, useRecomendaciones } from '@/hooks/useDatos';
import { usePersistente } from '@/hooks/usePersistente';
import { Cargando, ChipMarca, ErrorBox, Pildora, Select, Tarjeta } from '@/components/shared/Ui';
import { ars, campanaCorta, fecha, signo } from '@/utils/formato';
import { mensajeError } from '@/utils/errores';
import { calcularImpacto, fechaResultado, indicadores, MIN_DIAS_DESPUES, variacion, type ImpactoTarjeta, type Veredicto } from '@/utils/impacto';

const VEREDICTO: Record<Veredicto, { label: string; tono: 'verde' | 'rojo' | 'gris' | 'azul' }> = {
  positivo: { label: 'Positivo', tono: 'verde' },
  negativo: { label: 'Negativo', tono: 'rojo' },
  neutro: { label: 'Sin cambio claro', tono: 'gris' },
  midiendo: { label: 'Midiendo', tono: 'azul' },
  sin_datos: { label: 'Sin datos', tono: 'gris' },
};
const MEDIDA = (x: ImpactoTarjeta) => x.juicio.veredicto === 'positivo' || x.juicio.veredicto === 'negativo' || x.juicio.veredicto === 'neutro';

const dec = (n: number) => n.toLocaleString('es-AR', { maximumFractionDigits: 1 });
const porc1 = (n: number | null) => (n === null ? '—' : (n * 100).toLocaleString('es-AR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%');

/** Un indicador antes → después, con la variación en verde o rojo según convenga que suba o baje. */
function Dato({ etiqueta, antes, despues, v, bueno }: { etiqueta: string; antes: string; despues: string; v: number | null; bueno?: 'sube' | 'baja' }) {
  const tono = !bueno || v === null || Math.abs(v) < 0.1 ? 'text-mc-grey' : (v > 0) === (bueno === 'sube') ? 'text-emerald-700' : 'text-red-700';
  return (
    <div className="rounded-lg bg-mc-tint px-3 py-2">
      <div className="text-[10px] font-bold uppercase tracking-[0.12em] text-mc-grey">{etiqueta}</div>
      <div className="mt-0.5 font-mono text-[13px] text-mc-navy">
        {antes} <span className="text-mc-grey">→</span> {despues}
      </div>
      <div className={`font-mono text-[12px] font-semibold ${tono}`}>{signo(v)}</div>
    </div>
  );
}

function Optimizacion({ x, campana }: { x: ImpactoTarjeta; campana: string }) {
  const v = VEREDICTO[x.juicio.veredicto];
  const a = indicadores(x.antes!);
  const d = indicadores(x.despues!);
  return (
    <Tarjeta className="p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-1.5 text-[12px] text-mc-grey">
          <ChipMarca marca={x.rec.marca} />
          <span className="font-semibold text-mc-navy">{campanaCorta(campana)}</span>
        </div>
        <div className="flex items-center gap-2">
          {x.juicio.senalDebil && <span className="text-[11px] italic text-mc-grey">pocos clics: vale la dirección, no el número</span>}
          <Pildora tono={v.tono}>{v.label}</Pildora>
        </div>
      </div>
      <h3 className="mt-2 text-[15px] font-semibold leading-snug text-mc-navy">{x.rec.titulo}</h3>
      <p className="mt-1 text-[12px] text-mc-grey">
        Cargada en Ads el {fecha(x.ultimoCambio ?? x.fechaHecha)} · {x.despues!.dias} días después contra {x.antes!.dias} días antes
      </p>
      <p className="mt-3 text-[13px] text-mc-ink">{x.juicio.razones.join(' · ')}.</p>
      <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-5">
        <Dato etiqueta="Gasto por día" antes={ars(a.costeDia)} despues={ars(d.costeDia)} v={variacion(a.costeDia, d.costeDia)} />
        <Dato etiqueta="Clics por día" antes={dec(a.clicsDia)} despues={dec(d.clicsDia)} v={variacion(a.clicsDia, d.clicsDia)} bueno="sube" />
        <Dato etiqueta="CTR" antes={porc1(a.ctr)} despues={porc1(d.ctr)} v={variacion(a.ctr, d.ctr)} bueno="sube" />
        <Dato etiqueta="CPC" antes={a.cpc === null ? '—' : ars(a.cpc)} despues={d.cpc === null ? '—' : ars(d.cpc)} v={variacion(a.cpc, d.cpc)} bueno="baja" />
        <Dato etiqueta="Conversiones" antes={dec(x.antes!.conversiones)} despues={dec(x.despues!.conversiones)} v={variacion(a.convDia, d.convDia)} bueno="sube" />
      </div>
    </Tarjeta>
  );
}

export default function Impacto() {
  const recs = useRecomendaciones('SEM');
  const camp = useCampanas();
  const met = useMetricasDia(3);
  const cambios = useCambiosAds();
  const [eventos, setEventos] = useState<Evento[] | null>(null);
  const [errorEv, setErrorEv] = useState<string | null>(null);
  const [cliente, setCliente] = usePersistente('impacto:cliente', '');
  const [pais, setPais] = usePersistente('impacto:pais', '');
  const [indice, setIndice] = useState(0);

  const hechas = useMemo(() => recs.datos.filter((r) => r.estado === 'hecha'), [recs.datos]);
  const idsHechas = useMemo(() => hechas.map((r) => r.id).sort().join(','), [hechas]);
  useEffect(() => {
    if (recs.cargando) return;
    let vivo = true;
    listarEventosDe(idsHechas ? idsHechas.split(',') : [])
      .then((e) => vivo && setEventos(e))
      .catch((e: unknown) => vivo && setErrorEv(mensajeError(e)));
    return () => {
      vivo = false;
    };
  }, [idsHechas, recs.cargando]);

  const porCampana = useMemo(() => new Map(camp.datos.map((c) => [c.id, c])), [camp.datos]);
  const todas = useMemo(
    () => (eventos ? calcularImpacto({ recs: hechas, eventos, cambios: cambios.datos, metricas: met.datos }) : []),
    [hechas, eventos, cambios.datos, met.datos],
  );
  const unidad = (x: ImpactoTarjeta) => porCampana.get(x.campanaId)?.unidad ?? '—';
  const delCliente = todas.filter((x) => !cliente || x.rec.marca === cliente);
  const medidas = delCliente.filter(MEDIDA);
  const paises = [...new Set(medidas.map(unidad))].sort();
  const paisActivo = paises.includes(pais) ? pais : (paises[0] ?? '');
  const lista = medidas.filter((x) => unidad(x) === paisActivo);
  const actual = lista[Math.min(indice, lista.length - 1)];
  const enMedicion = delCliente.filter((x) => !MEDIDA(x));
  const proxima = enMedicion.map(fechaResultado).sort()[0];

  useEffect(() => setIndice(0), [paisActivo, cliente]);

  const error = recs.error || camp.error || met.error || cambios.error || errorEv;
  if (error) return <ErrorBox mensaje={error} />;
  if (recs.cargando || camp.cargando || met.cargando || cambios.cargando || !eventos) return <Cargando />;

  const filtroCliente = (
    <Select
      ariaLabel="Cliente"
      valor={cliente}
      onChange={setCliente}
      todo="Todos los clientes"
      opciones={MARCAS.map((m) => ({ id: m.id, label: m.label }))}
    />
  );

  if (!medidas.length) {
    return (
      <div className="animate-fade-in space-y-4">
        <div className="flex">{filtroCliente}</div>
        <Tarjeta className="flex flex-col items-center px-6 py-14 text-center">
          <Hourglass className="h-8 w-8 text-mc-blue" />
          <h2 className="mt-3 text-lg font-semibold text-mc-navy">Próximamente</h2>
          <p className="mt-1 max-w-md text-[13px] text-mc-grey">
            Cada optimización hecha muestra su resultado cuando junta {MIN_DIAS_DESPUES} días de datos después del cambio.
            {enMedicion.length > 0 && proxima && ` Hay ${enMedicion.length} en medición; la primera tiene resultado a partir del ${fecha(proxima)}.`}
          </p>
        </Tarjeta>
      </div>
    );
  }

  return (
    <div className="animate-fade-in space-y-4">
      <div className="flex flex-wrap items-center gap-2 rounded-card bg-mc-sup px-3 py-2.5 shadow-card">
        {filtroCliente}
        <div className="flex flex-wrap gap-1.5" role="tablist" aria-label="País">
          {paises.map((p) => {
            const n = medidas.filter((x) => unidad(x) === p).length;
            const activo = p === paisActivo;
            return (
              <button
                key={p}
                type="button"
                role="tab"
                aria-selected={activo}
                onClick={() => setPais(p)}
                className={`rounded-full px-3 py-1 text-[12.5px] font-medium ring-1 transition ${
                  activo ? 'bg-mc-fuerte text-white ring-mc-fuerte' : 'bg-mc-sup text-mc-ink ring-mc-hair hover:bg-mc-tint'
                }`}
              >
                {p} <span className="font-mono text-[11px] opacity-70">{n}</span>
              </button>
            );
          })}
        </div>
        {enMedicion.length > 0 && <span className="ml-auto text-[12px] text-mc-grey">{enMedicion.length} más en medición</span>}
      </div>

      {actual && (
        <>
          <div className="flex items-center gap-2">
            <button
              type="button"
              aria-label="Anterior"
              disabled={indice === 0}
              onClick={() => setIndice((i) => i - 1)}
              className="rounded-lg border border-mc-hair bg-mc-sup p-1.5 text-mc-navy transition hover:bg-mc-tint disabled:opacity-30"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <select
              aria-label="Optimización"
              value={actual.rec.id}
              onChange={(e) => setIndice(lista.findIndex((x) => x.rec.id === e.target.value))}
              className="min-w-0 flex-1 truncate rounded-lg border border-mc-hair bg-mc-sup px-2.5 py-1.5 text-sm text-mc-navy focus:border-mc-blue focus:outline-none"
            >
              {lista.map((x, i) => (
                <option key={x.rec.id} value={x.rec.id}>
                  {i + 1}. {campanaCorta(porCampana.get(x.campanaId)?.nombre ?? '')} — {VEREDICTO[x.juicio.veredicto].label}
                </option>
              ))}
            </select>
            <span className="font-mono text-[12px] text-mc-grey">
              {lista.indexOf(actual) + 1} de {lista.length}
            </span>
            <button
              type="button"
              aria-label="Siguiente"
              disabled={indice >= lista.length - 1}
              onClick={() => setIndice((i) => i + 1)}
              className="rounded-lg border border-mc-hair bg-mc-sup p-1.5 text-mc-navy transition hover:bg-mc-tint disabled:opacity-30"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
          <Optimizacion x={actual} campana={porCampana.get(actual.campanaId)?.nombre ?? '—'} />
        </>
      )}
    </div>
  );
}
