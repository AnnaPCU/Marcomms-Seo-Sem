/**
 * Presupuesto vs. gasto por cliente → país → campaña → grupo, por mes o por día, con semáforo y barra de consumo,
 * y la vista «Día a día»: cada día contra el presupuesto diario (VistaDiaria). Arriba se elige el mes (por defecto, el
 * último cerrado; también los anteriores, desde feb 2026) o la vista «Histórico» con la evolución mes a mes (VistaHistorica).
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
import { mesPorDefecto } from '@/utils/historico';
import { armarArbol, consumoMes, diasDelMes, resumir, ritmo, semaforo, type CampanaGasto, type GrupoGasto, type Nodo } from '@/utils/presupuesto';
import PanelRotacion from './PanelRotacion';
import { BarraConsumo, ChipDesvio } from './Semaforo';
import VistaDiaria from './VistaDiaria';
import VistaHistorica from './VistaHistorica';

type Vista = 'mes' | 'historico';
type Modo = 'mes' | 'dia' | 'calendario';
const MODOS: Modo[] = ['mes', 'dia', 'calendario'];
const COLUMNAS = 'grid grid-cols-[18px_minmax(0,1fr)_112px_112px_minmax(150px,200px)_76px_52px_40px] items-center gap-3';

function Fila({
  n,
  modo,
  dias,
  diasMes,
  abiertos,
  alternar,
}: {
  n: Nodo;
  modo: Modo;
  dias: number;
  diasMes: number;
  abiertos: Set<string>;
  alternar: (k: string) => void;
}) {
  const abierto = abiertos.has(n.clave);
  const r = ritmo(n.coste, n.presDia, dias);
  const sem = semaforo(n.coste, n.presDia, dias);
  const pres = n.presDia === null ? null : modo === 'mes' ? n.presDia * diasMes : n.presDia;
  const gasto = modo === 'mes' ? n.coste : n.coste / Math.max(dias, 1);
  const barra = modo === 'mes' ? consumoMes(n.coste, n.presDia, diasMes) : r;
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
        <span>{n.nivel < 4 && <BarraConsumo valor={barra} semaforo={sem} marca={modo === 'mes' && n.nivel === 3 ? dias / diasMes : undefined} />}</span>
        <span className="text-center">{n.nivel < 4 && <ChipDesvio coste={n.coste} ritmo={r} estado={n.nivel === 3 ? n.estado : undefined} />}</span>
        <span className="text-right font-mono">{entero(n.clics)}</span>
        <span className={`text-right font-mono ${n.conv ? 'font-semibold text-mc-blue' : 'text-mc-grey'}`}>{Math.round(n.conv)}</span>
      </div>
      {abierto && n.hijos.map((h) => <Fila key={h.clave} n={h} modo={modo} dias={dias} diasMes={diasMes} abiertos={abiertos} alternar={alternar} />)}
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

  const meses = useMemo(() => [...new Set(met.datos.map((m) => m.mes))].sort().reverse(), [met.datos]);
  const enCurso = mesActual();
  const porDefecto = mesPorDefecto(meses, enCurso);
  const mes = mesElegido || porDefecto;
  const delMes = useMemo(() => met.datos.filter((m) => m.mes === mes), [met.datos, mes]);
  const dias = Math.max(...delMes.map((m) => m.dias ?? 0), 0) || 1;
  const hasta = delMes.find((m) => m.hasta)?.hasta ?? null;
  const diasMes = mes ? diasDelMes(mes) : 30;

  const campanas: CampanaGasto[] = useMemo(() => {
    const porId = new Map(delMes.map((m) => [m.campanaId, m]));
    // Un mes cerrado muestra las campañas que tuvieron actividad; el mes en curso, además, las activas sin gasto todavía.
    return camp.datos
      .filter((c) => porId.has(c.id) || (mes === enCurso && c.cuenta === 'actual'))
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
  }, [camp.datos, delMes, mes, enCurso]);
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
  const modoVer: Modo = modo === 'calendario' && !hayDiario ? 'mes' : modo;

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
            <Select
              etiqueta="Período"
              ariaLabel="Mes"
              valor={mesElegido === porDefecto ? '' : mesElegido}
              onChange={setMes}
              todo={`${mesCorto(porDefecto)}${porDefecto < enCurso ? ' (último cerrado)' : ''}`}
              opciones={meses
                .filter((m) => m !== porDefecto)
                .map((m) => ({ id: m, label: m === enCurso ? `${mesCorto(m)} (en curso)` : mesCorto(m) }))}
            />
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
        <p className="text-xs text-mc-grey">
          {vista === 'mes'
            ? `Datos del ${fecha(delMes[0].desde)} al ${fecha(hasta)} · ${dias} de ${diasMes} días · API de Google Ads`
            : `${mesCorto(meses[meses.length - 1])} a ${mesCorto(meses[0])} · ${meses.length} meses · API de Google Ads`}
        </p>
      </div>

      {vista === 'historico' ? (
        <VistaHistorica campanas={refsHistoricas} metricas={met.datos} mesEnCurso={enCurso} />
      ) : (
        <>
          <PanelRotacion r={resumen} clientes={arbol} mes={mes} dias={dias} diasMes={diasMes} />

          <section>
            <SeccionTitulo meta={modoVer === 'calendario' ? 'cada día contra el presupuesto diario' : 'clic en cada fila para abrirla'}>
              {modoVer === 'calendario' ? 'Día a día' : 'Detalle por cliente, país, campaña y grupo'}
            </SeccionTitulo>
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <div className="inline-flex overflow-hidden rounded-lg border border-mc-hair bg-mc-sup text-sm">
                {MODOS.map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => setModo(m)}
                    disabled={m === 'calendario' && !hayDiario}
                    title={m === 'calendario' && !hayDiario ? 'No hay gasto por día cargado para este mes' : undefined}
                    className={`px-3 py-1.5 font-medium transition disabled:cursor-not-allowed disabled:opacity-40 ${modoVer === m ? 'bg-mc-fuerte text-white' : 'text-mc-ink hover:bg-mc-tint'}`}
                  >
                    {m === 'mes' ? `Mes (${mesCorto(mes)})` : m === 'dia' ? 'Promedio por día' : 'Día a día'}
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

            {modoVer === 'calendario' ? (
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
                  {modoVer === 'mes' && (
                    <span>
                      <b className="text-mc-navy">|</b> dónde debería estar el consumo al día {dias}
                    </span>
                  )}
                </div>

                <Tarjeta className="overflow-x-auto">
                  <div className="min-w-[860px]">
                    <div className={`${COLUMNAS} px-4 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-mc-grey`}>
                      <span />
                      <span>Nivel</span>
                      <span className="text-right">{modoVer === 'mes' ? `Presup. × ${diasMes} d` : 'Presup. / día'}</span>
                      <span className="text-right">{modoVer === 'mes' ? 'Gasto del mes' : 'Gasto / día'}</span>
                      <span>{modoVer === 'mes' ? 'Consumo del presupuesto (0–100%)' : 'Uso del presupuesto diario'}</span>
                      <span className="text-center">Desvío</span>
                      <span className="text-right">Clics</span>
                      <span className="text-right">Conv.</span>
                    </div>
                    {arbol.map((n) => (
                      <Fila key={n.clave} n={n} modo={modoVer} dias={dias} diasMes={diasMes} abiertos={abiertos} alternar={alternar} />
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
