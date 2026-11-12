/**
 * Presupuesto vs. gasto por cliente → país → campaña → grupo, con semáforo y barra de consumo, en tres modos: el mes,
 * «Cada 10 días» (VistaDecenas: tramos 1–10, 11–20 y 21–fin contra su presupuesto) y «Día a día» (VistaDiaria). Arriba se
 * elige el mes (por defecto, el actual: se arma con el gasto diario mientras no tiene fila mensual) o la vista
 * «Histórico» con la evolución mes a mes (VistaHistorica).
 * Réplica en vivo del informe «Gasto Google Ads por cliente» del proyecto de análisis.
 */
import { useMemo } from 'react';
import { usePersistente, usePersistenteSet } from '@/hooks/usePersistente';
import { ChevronRight } from 'lucide-react';
import { MARCA_BY_ID, MARCAS } from '@/constants/estados';
import { useCampanas, useGrupos, useMetricas, useMetricasDia, useMetricasGrupo } from '@/hooks/useDatos';
import { ErrorBox, SeccionTitulo, Select, Tarjeta, Vacio } from '@/components/shared/Ui';
import { EsqueletoPresupuesto } from '@/components/shared/Loader';
import { ars, campanaCorta, entero, fecha, mesActual, mesCorto } from '@/utils/formato';
import { mesIncompleto, mesPorDefecto } from '@/utils/historico';
import type { MetricaMes } from '@/services/metricas';
import {
  armarArbol, consumoMes, decenasDelMes, diasDelMes, gastoPorDecena, mesDesdeDiario, resumir, ritmo, semaforo, ultimoDiaConDatos,
  type CampanaGasto, type GrupoGasto, type Nodo,
} from '@/utils/presupuesto';
import PanelRotacion from './PanelRotacion';
import { BarraConsumo, ChipDesvio } from './Semaforo';
import VistaDecenas from './VistaDecenas';
import VistaDiaria from './VistaDiaria';
import VistaHistorica from './VistaHistorica';

type Vista = 'mes' | 'historico';
type Modo = 'mes' | 'decena' | 'calendario';
const MODOS: Modo[] = ['mes', 'decena', 'calendario'];
const ETIQUETA_MODO: Record<Modo, string> = { mes: 'Mes', decena: 'Cada 10 días', calendario: 'Día a día' };
const COLUMNAS = 'grid grid-cols-[18px_minmax(0,1fr)_112px_112px_minmax(150px,200px)_76px_52px_40px] items-center gap-3';

function Fila({
  n,
  dias,
  diasMes,
  abiertos,
  alternar,
}: {
  n: Nodo;
  dias: number;
  diasMes: number;
  abiertos: Set<string>;
  alternar: (k: string) => void;
}) {
  const abierto = abiertos.has(n.clave);
  const r = ritmo(n.coste, n.presDia, dias);
  const sem = semaforo(n.coste, n.presDia, dias);
  const pres = n.presDia === null ? null : n.presDia * diasMes;
  const gasto = n.coste;
  const barra = consumoMes(n.coste, n.presDia, diasMes);
  const sangria = ['', 'pl-0', 'pl-5', 'pl-10', 'pl-[60px]'][n.nivel];
  const fondo =
    n.nivel === 1
      ? 'border-l-4 border-l-mc-navy bg-mc-tint2 font-bold'
      : n.nivel === 2
        ? 'border-l-4 border-l-mc-blue bg-mc-tint font-semibold'
        : 'border-l-4 border-l-transparent bg-mc-sup';
  const nombre = n.nivel === 1 ? (MARCA_BY_ID[n.nombre as keyof typeof MARCA_BY_ID]?.label ?? n.nombre) : n.nivel === 3 ? campanaCorta(n.nombre) : n.nombre;
  const detalle =
    n.nivel === 1
      ? `${n.hijos.length} países`
      : n.nivel === 2
        ? `${n.hijos.length} campañas`
        : n.nivel === 3 && n.hijos.length
          ? `${n.hijos.length} grupos`
          : '';
  return (
    <>
      <div
        className={`${COLUMNAS} border-t border-mc-tint2 px-4 py-2 text-[13px] ${fondo} ${n.hijos.length ? 'cursor-pointer hover:bg-mc-tint' : ''}`}
        onClick={() => n.hijos.length && alternar(n.clave)}
      >
        <span className="text-mc-grey">{n.hijos.length ? <ChevronRight size={14} className={`transition ${abierto ? 'rotate-90' : ''}`} /> : null}</span>
        <span className={`truncate text-mc-navy ${sangria}`} title={n.nombre}>
          {nombre} {detalle && <span className="ml-1 text-[11px] font-normal text-mc-grey">{detalle}</span>}
          {n.cuenta === 'anterior' && (
            <span className="ml-1.5 rounded bg-mc-tint2 px-1 text-[10px] font-normal text-mc-grey" title="Cuenta «Peterson Technologies», facturada en euros y pasada a pesos">
              cuenta anterior
            </span>
          )}
        </span>
        <span className="text-right font-mono text-mc-grey">{pres === null ? '' : ars(pres)}</span>
        <span className="text-right font-mono text-mc-navy">{ars(gasto)}</span>
        <span>{n.nivel < 4 && <BarraConsumo valor={barra} semaforo={sem} marca={n.nivel === 3 ? dias / diasMes : undefined} />}</span>
        <span className="text-center">{n.nivel < 4 && <ChipDesvio coste={n.coste} ritmo={r} estado={n.nivel === 3 ? n.estado : undefined} />}</span>
        <span className="text-right font-mono">{entero(n.clics)}</span>
        <span className={`text-right font-mono ${n.conv ? 'font-semibold text-mc-blue' : 'text-mc-grey'}`}>{Math.round(n.conv)}</span>
      </div>
      {abierto && n.hijos.map((h) => <Fila key={h.clave} n={h} dias={dias} diasMes={diasMes} abiertos={abiertos} alternar={alternar} />)}
    </>
  );
}

export default function VistaPresupuesto() {
  const camp = useCampanas();
  const grupos = useGrupos();
  const met = useMetricas();
  const metG = useMetricasGrupo();
  const metD = useMetricasDia();
  // todo lo que elige la persona se recuerda al refrescar o volver a la pestaña
  const [vista, setVista] = usePersistente<Vista>('presupuesto:vista', 'mes');
  const [modo, setModo] = usePersistente<Modo>('presupuesto:modo', 'mes');
  const [mesElegido, setMes] = usePersistente('presupuesto:mes', '');
  const [cliente, setCliente] = usePersistente('presupuesto:cliente', '');
  const [pais, setPais] = usePersistente('presupuesto:pais', '');
  const [q, setQ] = usePersistente('presupuesto:busqueda', '');
  const [abiertos, setAbiertos] = usePersistenteSet('presupuesto:abiertos', MARCAS.map((m) => m.id));

  const enCurso = mesActual();
  // Meses con fila mensual y, para el mes en curso (o un mes sin fila mensual todavía), los totales armados con el
  // gasto diario: así el mes actual se ve desde el primer día cargado, sin esperar el cierre.
  const metMes: MetricaMes[] = useMemo(() => {
    const conDiario = [...new Set(metD.datos.map((d) => d.fecha.slice(0, 7)))];
    const reemplazar = conDiario.filter((m) => {
      const mensual = met.datos.filter((x) => x.mes === m);
      if (!mensual.length) return true;
      const hastaMensual = mensual.reduce((h, x) => (x.hasta && x.hasta > h ? x.hasta : h), '');
      return m === enCurso && (ultimoDiaConDatos(metD.datos, m) ?? '') > hastaMensual;
    });
    return [...met.datos.filter((x) => !reemplazar.includes(x.mes)), ...reemplazar.flatMap((m) => mesDesdeDiario(metD.datos, m))];
  }, [met.datos, metD.datos, enCurso]);
  const meses = useMemo(() => [...new Set(metMes.map((m) => m.mes))].sort().reverse(), [metMes]);
  // último día con datos de cada mes: un mes ya terminado que no llega a fin de mes se marca incompleto
  const hastaPorMes = useMemo(() => {
    const h = new Map<string, string | null>();
    for (const m of metMes) if (m.hasta && (!h.get(m.mes) || m.hasta > h.get(m.mes)!)) h.set(m.mes, m.hasta);
    return h;
  }, [metMes]);
  // por defecto, el mes actual; si todavía no tiene datos, el último cerrado completo
  const porDefecto = meses.includes(enCurso) ? enCurso : mesPorDefecto(meses, enCurso, hastaPorMes);
  const mes = mesElegido && meses.includes(mesElegido) ? mesElegido : porDefecto;
  const delMes = useMemo(() => metMes.filter((m) => m.mes === mes), [metMes, mes]);
  // los cuatro meses más nuevos van como botones; el resto, en «Anteriores…»
  const recientes = [...meses.slice(0, 4)].reverse();
  const anteriores = meses.slice(4);
  const etiquetaMes = (m: string) =>
    m === enCurso
      ? `${mesCorto(m)} (en curso)`
      : mesIncompleto(m, hastaPorMes.get(m), enCurso)
        ? `${mesCorto(m)} (incompleto: hasta ${fecha(hastaPorMes.get(m) ?? null)})`
        : mesCorto(m);
  const dias = Math.max(...delMes.map((m) => m.dias ?? 0), 0) || 1;
  const hasta = delMes.find((m) => m.hasta)?.hasta ?? null;
  const diasMes = mes ? diasDelMes(mes) : 30;

  const campanas: CampanaGasto[] = useMemo(() => {
    const porId = new Map(delMes.map((m) => [m.campanaId, m]));
    // Google no devuelve filas de una campaña sin impresiones, así que una activa que no publicó desaparecería justo
    // cuando más hay que verla (PrimusGFS en oct 2026: ARS 15.000/día reservados y 0 impresiones). Se muestran las que
    // tuvieron actividad y, además, las activas de la cuenta actual que ya existían ese mes (con datos en ese mes o
    // antes); en el mes en curso, todas las activas.
    const existia = new Set(metMes.filter((m) => m.mes <= mes).map((m) => m.campanaId));
    return camp.datos
      .filter((c) => porId.has(c.id) || (c.cuenta === 'actual' && c.estado === 'ENABLED' && (mes === enCurso || existia.has(c.id))))
      .map((c) => {
      const m = porId.get(c.id);
      return {
        id: c.id,
        nombre: c.nombre,
        marca: c.marca,
        unidad: c.unidad,
        estado: c.estado,
        presupuestoDia: c.presupuestoDia,
        coste: m?.coste ?? 0,
        clics: m?.clics ?? 0,
        conv: m?.conversiones ?? 0,
        impresiones: m?.impresiones ?? 0,
        cuenta: c.cuenta,
      };
    });
  }, [camp.datos, delMes, mes, enCurso, metMes]);
  const incompleto = mesIncompleto(mes, hasta, enCurso);
  // la vista histórica usa todo el catálogo (incluye campañas eliminadas y de la cuenta anterior)
  const refsHistoricas = useMemo(
    () => camp.datos.filter((c) => (!cliente || c.marca === cliente) && (!pais || c.unidad === pais)),
    [camp.datos, cliente, pais],
  );
  const paisesTodos = useMemo(
    () => [...new Set(camp.datos.filter((c) => !cliente || c.marca === cliente).map((c) => c.unidad))].sort(),
    [camp.datos, cliente],
  );
  const hayDiario = metD.datos.some((d) => d.fecha.startsWith(mes));
  // 'dia' (promedio por día) ya no existe: si quedó guardado, se ve el mes
  const modoVer: Modo = !MODOS.includes(modo) || (modo !== 'mes' && !hayDiario) ? 'mes' : modo;
  const decenas = useMemo(() => decenasDelMes(mes, ultimoDiaConDatos(metD.datos, mes)), [mes, metD.datos]);
  const gastoDecenas = useMemo(() => gastoPorDecena(metD.datos, mes), [metD.datos, mes]);

  const paises = useMemo(() => [...new Set(campanas.filter((c) => !cliente || c.marca === cliente).map((c) => c.unidad))].sort(), [campanas, cliente]);
  const texto = q.trim().toLowerCase();
  const nombreGrupo = useMemo(() => new Map(grupos.datos.map((g) => [g.id, g.nombre])), [grupos.datos]);
  const gruposMes: GrupoGasto[] = useMemo(
    () =>
      metG.datos
        .filter((g) => g.mes === mes)
        .map((g) => ({ campanaId: g.campanaId, nombre: nombreGrupo.get(g.grupoId) ?? '—', coste: g.coste, clics: g.clics, conv: g.conversiones })),
    [metG.datos, mes, nombreGrupo],
  );
  const visibles = useMemo(
    () =>
      campanas.filter(
        (c) =>
          (!cliente || c.marca === cliente) &&
          (!pais || c.unidad === pais) &&
          (!texto || c.nombre.toLowerCase().includes(texto) || gruposMes.some((g) => g.campanaId === c.id && g.nombre.toLowerCase().includes(texto))),
      ),
    [campanas, cliente, pais, texto, gruposMes],
  );
  const arbol = useMemo(
    () =>
      armarArbol(
        visibles,
        gruposMes,
        MARCAS.map((m) => m.id),
      ),
    [visibles, gruposMes],
  );
  const resumen = useMemo(() => resumir(visibles, dias, diasMes), [visibles, dias, diasMes]);

  const alternar = (k: string) =>
    setAbiertos((prev) => {
      const s = new Set(prev);
      if (s.has(k)) s.delete(k);
      else s.add(k);
      return s;
    });
  const expandirTodo = () => {
    const s = new Set<string>();
    const recorrer = (ns: Nodo[]) => ns.forEach((n) => (n.hijos.length && s.add(n.clave), recorrer(n.hijos)));
    recorrer(arbol);
    setAbiertos(s);
  };

  const error = camp.error || met.error || metG.error || metD.error;
  if (error) return <ErrorBox mensaje={error} />;
  if (camp.cargando || met.cargando) return <EsqueletoPresupuesto />;
  if (!delMes.length) return <Vacio>Todavía no hay gasto cargado. Corré scripts/publicar.py después de una extracción de Ads.</Vacio>;

  return (
    <div className="space-y-7 animate-fade-in">
      <div className="flex flex-wrap items-end justify-between gap-3 rounded-card bg-mc-sup px-4 py-3 shadow-card">
        <div className="flex flex-wrap items-end gap-3">
          <Select
            etiqueta="Cliente"
            ariaLabel="Cliente"
            valor={cliente}
            onChange={(v) => (setCliente(v), setPais(''))}
            todo="Todos los clientes"
            opciones={MARCAS.map((m) => ({ id: m.id, label: m.label }))}
          />
          <Select
            etiqueta="País"
            ariaLabel="País"
            valor={pais}
            onChange={setPais}
            todo="Todos los países"
            opciones={(vista === 'historico' ? paisesTodos : paises).map((p) => ({ id: p, label: p }))}
          />
          {vista === 'mes' && meses.length > 1 && (
            <div className="flex flex-col gap-1">
              <span className="text-[10px] font-bold uppercase tracking-[0.14em] text-mc-grey">Mes</span>
              <div className="flex items-center gap-1.5">
                <div className="inline-flex overflow-hidden rounded-lg border border-mc-hair bg-mc-sup text-sm" role="tablist" aria-label="Mes">
                  {recientes.map((m) => (
                    <button
                      key={m}
                      type="button"
                      role="tab"
                      aria-selected={m === mes}
                      onClick={() => setMes(m === porDefecto ? '' : m)}
                      title={etiquetaMes(m)}
                      className={`px-3 py-1.5 font-medium transition ${m === mes ? 'bg-mc-fuerte text-white' : 'text-mc-ink hover:bg-mc-tint'}`}
                    >
                      {mesCorto(m)}
                      {m === enCurso && <span className="ml-1 text-[10px] opacity-70">en curso</span>}
                      {m !== enCurso && mesIncompleto(m, hastaPorMes.get(m), enCurso) && <span className="ml-1 text-[10px] opacity-70">incompleto</span>}
                    </button>
                  ))}
                </div>
                {anteriores.length > 0 && (
                  <Select
                    ariaLabel="Meses anteriores"
                    valor={anteriores.includes(mes) ? mes : ''}
                    onChange={(v) => setMes(v)}
                    todo="Anteriores…"
                    opciones={anteriores.map((m) => ({ id: m, label: etiquetaMes(m) }))}
                  />
                )}
              </div>
            </div>
          )}
          <div className="flex flex-col gap-1">
            <span className="text-[10px] font-bold uppercase tracking-[0.14em] text-mc-grey">Vista</span>
            <div className="inline-flex overflow-hidden rounded-lg border border-mc-hair bg-mc-sup text-sm">
              {(['mes', 'historico'] as Vista[]).map((v) => (
                <button
                  key={v}
                  type="button"
                  onClick={() => setVista(v)}
                  className={`px-3 py-1.5 font-medium transition ${vista === v ? 'bg-mc-fuerte text-white' : 'text-mc-ink hover:bg-mc-tint'}`}
                >
                  {v === 'mes' ? 'Un mes' : 'Histórico'}
                </button>
              ))}
            </div>
          </div>
        </div>
        {vista === 'mes' && incompleto && (
          <p role="alert" className="w-full rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
            {mesCorto(mes)} ya terminó, pero los datos llegan solo hasta el {fecha(hasta)}: falta correr la extracción de cierre de
            mes. Los totales de este mes están incompletos.
          </p>
        )}
        <p className="text-xs text-mc-grey">
          {vista === 'mes'
            ? `Datos del ${fecha(delMes[0].desde)} al ${fecha(hasta)} · ${dias} de ${diasMes} días · API de Google Ads`
            : `${mesCorto(meses[meses.length - 1])} a ${mesCorto(meses[0])} · ${meses.length} meses · API de Google Ads`}
        </p>
      </div>

      {vista === 'historico' ? (
        <VistaHistorica campanas={refsHistoricas} metricas={metMes} mesEnCurso={enCurso} />
      ) : (
        <>
          <PanelRotacion r={resumen} clientes={arbol} mes={mes} dias={dias} diasMes={diasMes} />

          <section>
            <SeccionTitulo
              meta={modoVer === 'calendario' ? 'cada día contra el presupuesto diario' : modoVer === 'decena' ? 'cada tramo contra su presupuesto' : 'clic en cada fila para abrirla'}
            >
              {modoVer === 'calendario' ? 'Día a día' : `Detalle por cliente, país, campaña${modoVer === 'mes' ? ' y grupo' : ''} · ${mesCorto(mes)}`}
            </SeccionTitulo>
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <div className="inline-flex overflow-hidden rounded-lg border border-mc-hair bg-mc-sup text-sm">
                {MODOS.map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => setModo(m)}
                    disabled={m !== 'mes' && !hayDiario}
                    title={m !== 'mes' && !hayDiario ? 'No hay gasto por día cargado para este mes' : undefined}
                    className={`px-3 py-1.5 font-medium transition disabled:cursor-not-allowed disabled:opacity-40 ${modoVer === m ? 'bg-mc-fuerte text-white' : 'text-mc-ink hover:bg-mc-tint'}`}
                  >
                    {ETIQUETA_MODO[m]}
                  </button>
                ))}
              </div>
              <input
                aria-label="Buscar campaña o grupo"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Buscar campaña o grupo…"
                className="min-w-[180px] flex-1 rounded-lg border border-mc-hair bg-mc-sup px-2.5 py-1.5 text-sm focus:border-mc-blue focus:outline-none"
              />
              {modoVer !== 'calendario' && (
                <button
                  type="button"
                  onClick={expandirTodo}
                  className="rounded-lg border border-mc-hair bg-mc-sup px-3 py-1.5 text-sm text-mc-navy hover:bg-mc-tint"
                >
                  Expandir todo
                </button>
              )}
            </div>

            {modoVer === 'decena' ? (
              metD.cargando ? (
                <EsqueletoPresupuesto />
              ) : (
                <VistaDecenas
                  arbol={arbol}
                  mes={mes}
                  diasMes={diasMes}
                  decenas={decenas}
                  gasto={gastoDecenas}
                  abiertos={abiertos}
                  alternar={alternar}
                />
              )
            ) : modoVer === 'calendario' ? (
              <>
                <div className="mb-3 flex flex-wrap gap-4 text-xs text-mc-grey">
                  <span>
                    <b className="text-red-700">■ Rojo</b> gastó más de un 5% por encima del presupuesto del día
                  </span>
                  <span>
                    <b className="text-red-400">■ Rojo claro</b> campaña activa que no gastó nada
                  </span>
                  <span>
                    <b className="text-emerald-700">■ Verde</b> dentro del presupuesto
                  </span>
                  <span>
                    <b>■ Gris</b> sin presupuesto activo
                  </span>
                </div>
                {metD.cargando ? <EsqueletoPresupuesto /> : <VistaDiaria key={mes} mesInicial={mes} campanas={visibles} dias={metD.datos} />}
                <p className="mt-3 text-xs text-mc-grey">
                  Presupuesto: el diario que tiene hoy cada campaña en Google Ads; si se cambió durante el mes, los días anteriores se comparan contra el valor
                  actual. Google puede gastar hasta el doble del presupuesto en un día y lo compensa en el mes, así que un día en rojo aislado es normal; varios
                  seguidos indican que la campaña pide más presupuesto.
                </p>
              </>
            ) : (
              <>
                <div className="mb-3 flex flex-wrap gap-4 text-xs text-mc-grey">
                  <span>
                    <b className="text-emerald-700">● Verde</b> gasta dentro de su presupuesto diario
                  </span>
                  <span>
                    <b className="text-red-700">● Rojo</b> gasta más de un 5% por encima, o no gasta nada
                  </span>
                  <span>
                    <b>● Gris</b> sin presupuesto activo (pausada o eliminada)
                  </span>
                  <span>
                    <b className="text-mc-navy">|</b> dónde debería estar el consumo al día {dias}
                  </span>
                </div>

                <Tarjeta className="overflow-x-auto">
                  <div className="min-w-[860px]">
                    <div className={`${COLUMNAS} px-4 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-mc-grey`}>
                      <span />
                      <span>Nivel</span>
                      <span className="text-right">{`Presup. × ${diasMes} d`}</span>
                      <span className="text-right">Gasto del mes</span>
                      <span>Consumo del presupuesto (0–100%)</span>
                      <span className="text-center">Desvío</span>
                      <span className="text-right">Clics</span>
                      <span className="text-right">Conv.</span>
                    </div>
                    {arbol.map((n) => (
                      <Fila key={n.clave} n={n} dias={dias} diasMes={diasMes} abiertos={abiertos} alternar={alternar} />
                    ))}
                  </div>
                </Tarjeta>
                <p className="mt-3 text-xs text-mc-grey">
                  Presupuesto: el diario configurado en Google Ads, solo de campañas activas; en la vista mensual, × {diasMes} días. Consumo: gasto acumulado sobre
                  el presupuesto del mes completo. El semáforo compara el gasto por día (sobre {dias} días con datos) contra el presupuesto por día. Los grupos de
                  anuncios no tienen presupuesto propio.
                  {mes < enCurso &&
                    ' En un mes cerrado se compara contra el presupuesto de hoy (el tablero solo tiene el presupuesto actual de cada campaña): sirve de referencia. Las campañas de la cuenta anterior no tienen presupuesto cargado.'}
                </p>
              </>
            )}
          </section>
        </>
      )}
    </div>
  );
}
