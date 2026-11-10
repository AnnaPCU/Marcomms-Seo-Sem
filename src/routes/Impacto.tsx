/**
 * Impacto: qué se implementó de cada optimización SEM marcada como «hecha» y si el resultado fue positivo o negativo.
 * Cruza los ítems de la tarjeta con el historial de cambios de Google Ads y compara 28 días antes / después del cambio
 * real (utils/impacto.ts). «Hecha» quiere decir que se aplicó la mayor parte, no todo: por eso se muestra ítem por ítem.
 */
import { useEffect, useMemo, useState } from 'react';
import { CheckCircle2, CircleDashed, HelpCircle, TriangleAlert } from 'lucide-react';
import { MARCAS } from '@/constants/estados';
import { listarEventosDe, type Evento } from '@/services/recomendaciones';
import { useCambiosAds, useCampanas, useMetricasDia, useRecomendaciones } from '@/hooks/useDatos';
import { usePersistente } from '@/hooks/usePersistente';
import { Cargando, ChipMarca, ErrorBox, Intro, Kpi, Pildora, SeccionTitulo, Select, Tarjeta, Vacio } from '@/components/shared/Ui';
import { ars, campanaCorta, fecha, signo } from '@/utils/formato';
import { mensajeError } from '@/utils/errores';
import {
  calcularImpacto, DIAS_VENTANA, indicadores, MIN_DIAS_DESPUES, variacion, type ImpactoTarjeta, type ItemCruzado, type Veredicto, type Ventana,
} from '@/utils/impacto';

const VEREDICTO: Record<Veredicto, { label: string; tono: 'verde' | 'rojo' | 'gris' | 'azul' }> = {
  positivo: { label: 'Resultado positivo', tono: 'verde' },
  negativo: { label: 'Resultado negativo', tono: 'rojo' },
  neutro: { label: 'Sin cambio claro', tono: 'gris' },
  midiendo: { label: 'Midiendo', tono: 'azul' },
  sin_datos: { label: 'Sin datos', tono: 'gris' },
};

const corta = (f: string) => `${f.slice(8, 10)}/${f.slice(5, 7)}`;
const dec = (n: number) => n.toLocaleString('es-AR', { maximumFractionDigits: 1 });
const porc1 = (n: number | null) => (n === null ? '—' : (n * 100).toLocaleString('es-AR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%');

function etiquetaItem(i: ItemCruzado): string {
  if (i.tipo === 'negativa') return 'Negativa';
  if (i.tipo === 'keyword') return i.accion === 'pausar' ? 'Pausar' : 'Keyword';
  if (i.tipo === 'titulo') return 'Título';
  if (i.tipo === 'descripcion') return 'Descripción';
  if (i.tipo === 'grupo') return 'Grupo nuevo';
  if (/^https?:\/\//i.test(i.texto)) return 'URL final';
  return i.accion === 'decidir' ? 'Decidir' : 'Ajuste';
}

function IconoItem({ estado }: { estado: ItemCruzado['estado'] }) {
  if (estado === 'aplicado') return <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-600" aria-label="Aplicado en Ads" />;
  if (estado === 'a_criterio') return <HelpCircle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-600" aria-label="A criterio del equipo" />;
  return <CircleDashed className="mt-0.5 h-3.5 w-3.5 shrink-0 text-mc-grey" aria-label="No se ve en Ads" />;
}

function ListaItems({ items }: { items: ItemCruzado[] }) {
  const pasos = new Map<number, ItemCruzado[]>();
  for (const i of items) pasos.set(i.paso, [...(pasos.get(i.paso) ?? []), i]);
  return (
    <div className="space-y-2.5">
      {[...pasos.entries()].map(([n, lista]) => (
        <div key={n}>
          <div className="mb-1 text-[11px] font-semibold text-mc-navy">
            {n}. {lista[0].tituloPaso}
            <span className="ml-1.5 font-normal text-mc-grey">
              {lista.filter((x) => x.estado === 'aplicado').length} de {lista.filter((x) => x.estado !== 'a_criterio').length || lista.length}
            </span>
          </div>
          <ul className="space-y-0.5">
            {lista.map((i, k) => (
              <li key={k} className={`flex gap-1.5 text-[12px] leading-snug ${i.estado === 'no_visto' ? 'text-mc-grey' : 'text-mc-ink'}`}>
                <IconoItem estado={i.estado} />
                <span>
                  <span className="font-semibold">{etiquetaItem(i)}:</span> {i.texto}
                  {i.concordancia && (i.tipo === 'keyword' || i.tipo === 'negativa') && <span className="text-mc-grey"> ({i.concordancia})</span>}
                  {i.cambio && <span className="ml-1 font-mono text-[10px] text-mc-grey">{corta(i.cambio.fecha)}</span>}
                  {i.nota && <span className="block text-[11px] italic text-mc-grey">{i.nota}</span>}
                </span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

/** Con `parcial` (menos días que el mínimo) muestra los valores pero no la variación: dos días de fin de semana engañan. */
function Comparacion({ antes, despues, parcial }: { antes: Ventana; despues: Ventana; parcial: boolean }) {
  const a = indicadores(antes);
  const d = indicadores(despues);
  const filas: { label: string; a: string; d: string; v: number | null; bueno?: 'sube' | 'baja' }[] = [
    { label: 'Gasto por día', a: ars(a.costeDia), d: ars(d.costeDia), v: variacion(a.costeDia, d.costeDia) },
    { label: 'Clics por día', a: dec(a.clicsDia), d: dec(d.clicsDia), v: variacion(a.clicsDia, d.clicsDia) },
    { label: 'Impresiones por día', a: dec(a.imprDia), d: dec(d.imprDia), v: variacion(a.imprDia, d.imprDia) },
    { label: 'CTR', a: porc1(a.ctr), d: porc1(d.ctr), v: variacion(a.ctr, d.ctr), bueno: 'sube' },
    { label: 'CPC', a: a.cpc === null ? '—' : ars(a.cpc), d: d.cpc === null ? '—' : ars(d.cpc), v: variacion(a.cpc, d.cpc), bueno: 'baja' },
    { label: 'Conversiones', a: dec(antes.conversiones), d: dec(despues.conversiones), v: variacion(a.convDia, d.convDia), bueno: 'sube' },
  ];
  const tono = (f: (typeof filas)[number]) => {
    if (parcial || !f.bueno || f.v === null || Math.abs(f.v) < 0.1) return 'text-mc-grey';
    return (f.v > 0) === (f.bueno === 'sube') ? 'text-emerald-700' : 'text-red-700';
  };
  return (
    <table className="w-full text-[12px]">
      <thead>
        <tr className="text-left text-[10px] uppercase tracking-[0.1em] text-mc-grey">
          <th className="pb-1 font-semibold" />
          <th className="pb-1 text-right font-semibold">Antes<div className="font-mono normal-case tracking-normal">{corta(antes.desde)}–{corta(antes.hasta)} · {antes.dias} d</div></th>
          <th className="pb-1 text-right font-semibold">Después<div className="font-mono normal-case tracking-normal">{despues.dias ? `${corta(despues.desde)}–${corta(despues.hasta)} · ${despues.dias} d` : 'sin días'}</div></th>
          <th className="pb-1 text-right font-semibold">{parcial ? 'Var. (parcial)' : 'Var.'}</th>
        </tr>
      </thead>
      <tbody>
        {filas.map((f) => (
          <tr key={f.label} className="border-t border-mc-tint2">
            <td className="py-1 text-mc-ink">{f.label}</td>
            <td className="py-1 text-right font-mono text-mc-navy">{f.a}</td>
            <td className="py-1 text-right font-mono text-mc-navy">{despues.dias ? f.d : '—'}</td>
            <td className={`py-1 text-right font-mono font-semibold ${tono(f)}`}>{despues.dias && !parcial ? signo(f.v) : '—'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function FilaImpacto({ x, campana, unidad }: { x: ImpactoTarjeta; campana: string; unidad: string }) {
  const v = VEREDICTO[x.juicio.veredicto];
  const porc = x.verificables ? Math.round((x.aplicados / x.verificables) * 100) : null;
  return (
    <Tarjeta className="p-4">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-1.5 text-[12px] text-mc-grey">
            <ChipMarca marca={x.rec.marca} />
            <span>{unidad}</span>
            <span>·</span>
            <span className="font-semibold text-mc-navy">{campanaCorta(campana)}</span>
          </div>
          <h3 className="mt-1 text-[14px] font-semibold leading-snug text-mc-navy">{x.rec.titulo}</h3>
          <p className="mt-0.5 text-[12px] text-mc-grey">
            Marcada hecha el {fecha(x.fechaHecha)}
            {x.primerCambio
              ? ` · cargada en Ads ${x.primerCambio === x.ultimoCambio ? `el ${fecha(x.primerCambio)}` : `del ${fecha(x.primerCambio)} al ${fecha(x.ultimoCambio)}`}`
              : ' · ningún ítem visible en Ads'}
          </p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <Pildora tono={v.tono}>
            {v.label}
            {x.juicio.veredicto === 'midiendo' && x.despues ? ` (${x.despues.dias}/${MIN_DIAS_DESPUES} días)` : ''}
          </Pildora>
          {x.juicio.senalDebil && x.juicio.veredicto !== 'midiendo' && x.juicio.veredicto !== 'sin_datos' && (
            <span className="text-[10px] italic text-mc-grey">señal débil: menos de 10 clics</span>
          )}
        </div>
      </div>

      <div className="mt-3 grid gap-4 lg:grid-cols-2">
        <section>
          <div className="mb-2 flex items-center gap-2">
            <span className="text-[10px] font-bold uppercase tracking-[0.14em] text-mc-blue">Qué se implementó</span>
            <span className="text-[11px] text-mc-grey">
              {x.aplicados} de {x.verificables} ítems{porc !== null ? ` (${porc}%)` : ''}
            </span>
          </div>
          {porc !== null && (
            <div className="mb-3 h-1.5 overflow-hidden rounded-full bg-mc-tint2">
              <div className="h-full rounded-full bg-emerald-500" style={{ width: `${porc}%` }} />
            </div>
          )}
          <ListaItems items={x.items} />
        </section>
        <section>
          <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.14em] text-mc-blue">Antes vs. después</div>
          {x.antes && x.despues ? <Comparacion antes={x.antes} despues={x.despues} parcial={x.juicio.veredicto === 'midiendo'} /> : <p className="text-[12px] text-mc-grey">Sin datos diarios cargados.</p>}
          <ul className="mt-2 space-y-0.5 text-[12px] text-mc-ink">
            {x.juicio.razones.map((r) => (
              <li key={r}>· {r}</li>
            ))}
          </ul>
          {x.avisos.map((a) => (
            <p key={a} className="mt-2 flex gap-1.5 rounded-md bg-amber-50 px-2 py-1.5 text-[11px] text-amber-800">
              <TriangleAlert className="mt-0.5 h-3 w-3 shrink-0" />
              {a}
            </p>
          ))}
        </section>
      </div>

      {x.otrosCambios.length > 0 && (
        <details className="mt-3 border-t border-mc-tint2 pt-2">
          <summary className="cursor-pointer text-[12px] font-semibold text-mc-navy">
            Otros cambios en la campaña durante la implementación ({x.otrosCambios.length})
          </summary>
          <ul className="mt-1.5 space-y-0.5">
            {x.otrosCambios.map((c) => (
              <li key={c.id} className="text-[12px] text-mc-ink">
                <span className="mr-1.5 font-mono text-[10px] text-mc-grey">{corta(c.fecha)}</span>
                {c.resumen}
              </li>
            ))}
          </ul>
        </details>
      )}
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
  const [resultado, setResultado] = usePersistente('impacto:resultado', '');

  const hechas = useMemo(() => recs.datos.filter((r) => r.estado === 'hecha'), [recs.datos]);
  const idsHechas = useMemo(() => hechas.map((r) => r.id).sort().join(','), [hechas]);
  useEffect(() => {
    if (recs.cargando) return;
    let vivo = true;
    const ids = idsHechas ? idsHechas.split(',') : [];
    listarEventosDe(ids)
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
  const sinCampana = hechas.filter((r) => !r.campanaId).length;
  const paises = useMemo(
    () => [...new Set(todas.filter((x) => !cliente || x.rec.marca === cliente).map((x) => porCampana.get(x.campanaId)?.unidad).filter(Boolean) as string[])].sort(),
    [todas, cliente, porCampana],
  );
  const visibles = todas.filter(
    (x) =>
      (!cliente || x.rec.marca === cliente) &&
      (!pais || porCampana.get(x.campanaId)?.unidad === pais) &&
      (!resultado || x.juicio.veredicto === resultado || (resultado === 'midiendo' && x.juicio.veredicto === 'sin_datos')),
  );
  const cuenta = (v: Veredicto) => visibles.filter((x) => x.juicio.veredicto === v).length;
  const aplicados = visibles.reduce((s, x) => s + x.aplicados, 0);
  const verificables = visibles.reduce((s, x) => s + x.verificables, 0);
  const datosHasta = met.datos.reduce((m, d) => (d.fecha > m ? d.fecha : m), '');
  const cambiosHasta = cambios.datos.reduce((m, c) => (c.fecha > m ? c.fecha : m), '');

  const error = recs.error || camp.error || met.error || cambios.error || errorEv;
  if (error) return <ErrorBox mensaje={error} />;
  if (recs.cargando || camp.cargando || met.cargando || cambios.cargando || !eventos) return <Cargando texto="Cruzando las optimizaciones con Google Ads…" />;

  return (
    <div className="space-y-6 animate-fade-in">
      <Intro
        cifras={[
          { valor: datosHasta ? corta(datosHasta) : '—', etiqueta: 'Métricas hasta' },
          { valor: cambiosHasta ? corta(cambiosHasta.slice(0, 10)) : '—', etiqueta: 'Cambios hasta' },
        ]}
      >
        Cada optimización marcada como <b>hecha</b>, ítem por ítem contra el historial de cambios de Google Ads: qué se cargó de verdad y
        qué no. El resultado compara {DIAS_VENTANA} días antes del primer cambio con los días posteriores al último (mínimo {MIN_DIAS_DESPUES}),
        por día y por campaña.
        {sinCampana > 0 && ` ${sinCampana} hecha${sinCampana > 1 ? 's' : ''} sin campaña (planes de cuenta) no se mide${sinCampana > 1 ? 'n' : ''}.`}
      </Intro>

      <div className="flex flex-wrap items-end gap-3 rounded-card bg-mc-sup px-4 py-3 shadow-card">
        <Select
          etiqueta="Cliente"
          ariaLabel="Cliente"
          valor={cliente}
          onChange={(v) => (setCliente(v), setPais(''))}
          todo="Todos los clientes"
          opciones={MARCAS.map((m) => ({ id: m.id, label: m.label }))}
        />
        <Select etiqueta="País" ariaLabel="País" valor={pais} onChange={setPais} todo="Todos los países" opciones={paises.map((p) => ({ id: p, label: p }))} />
        <Select
          etiqueta="Resultado"
          ariaLabel="Resultado"
          valor={resultado}
          onChange={setResultado}
          todo="Todos los resultados"
          opciones={[
            { id: 'positivo', label: 'Positivo' },
            { id: 'negativo', label: 'Negativo' },
            { id: 'neutro', label: 'Sin cambio claro' },
            { id: 'midiendo', label: 'Midiendo' },
          ]}
        />
      </div>

      <section>
        <SeccionTitulo meta={`${visibles.length} optimizaciones hechas`}>Resumen</SeccionTitulo>
        <div className="grid grid-cols-2 gap-3 xl:grid-cols-5">
          <Kpi acento="noche" valor={verificables ? `${Math.round((aplicados / verificables) * 100)}%` : '—'} etiqueta="Ítems aplicados" nota={`${aplicados} de ${verificables} verificables en Ads`} />
          <Kpi acento="verde" valor={cuenta('positivo')} etiqueta="Positivas" />
          <Kpi acento="rojo" valor={cuenta('negativo')} etiqueta="Negativas" />
          <Kpi acento="gris" valor={cuenta('neutro')} etiqueta="Sin cambio claro" />
          <Kpi acento="azul" valor={cuenta('midiendo') + cuenta('sin_datos')} etiqueta="Midiendo" nota={`Menos de ${MIN_DIAS_DESPUES} días de datos después`} />
        </div>
      </section>

      <section>
        <SeccionTitulo meta="de la más reciente a la más vieja">Optimizaciones</SeccionTitulo>
        {visibles.length === 0 ? (
          <Vacio>No hay optimizaciones hechas con estos filtros.</Vacio>
        ) : (
          <div className="space-y-3">
            {visibles.map((x) => {
              const c = porCampana.get(x.campanaId);
              return <FilaImpacto key={x.rec.id} x={x} campana={c?.nombre ?? '—'} unidad={c?.unidad ?? '—'} />;
            })}
          </div>
        )}
      </section>

      <p className="text-[11px] leading-relaxed text-mc-grey">
        Cómo se lee: «hecha» quiere decir que se aplicó la mayor parte de la propuesta, no todo; por eso cada ítem dice si se ve cargado en
        Ads (✓), si no aparece (○) o si era una decisión o un ajuste que no se verifica solo (?). El resultado suma conversiones (pesan doble),
        CTR y CPC: cada uno cuenta si se mueve 10% o más. Bajar el gasto no es bueno ni malo por sí solo, porque muchas optimizaciones lo bajan
        a propósito. Con pocos clics o pocas conversiones la dirección sirve, el número no. Google guarda el historial de cambios 30 días: se
        extrae en el cierre de cada mes y queda guardado acá.
      </p>
    </div>
  );
}
