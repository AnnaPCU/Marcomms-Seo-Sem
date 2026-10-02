/**
 * Presupuesto vs. gasto por cliente → país → campaña → grupo, por mes o por día, con semáforo y barra de consumo,
 * y la vista «Día a día»: cada día contra el presupuesto diario (VistaDiaria).
 * Réplica en vivo del informe «Gasto Google Ads por cliente» del proyecto de análisis.
 */
import { useMemo, useState } from 'react';
import { ChevronRight } from 'lucide-react';
import { MARCA_BY_ID, MARCAS } from '@/constants/estados';
import { useCampanas, useGrupos, useMetricas, useMetricasDia, useMetricasGrupo } from '@/hooks/useDatos';
import { ErrorBox, SeccionTitulo, Select, Tarjeta, Vacio } from '@/components/shared/Ui';
import { EsqueletoPresupuesto } from '@/components/shared/Loader';
import { ars, campanaCorta, entero, fecha, mesCorto } from '@/utils/formato';
import { armarArbol, consumoMes, diasDelMes, resumir, ritmo, semaforo, type CampanaGasto, type GrupoGasto, type Nodo } from '@/utils/presupuesto';
import PanelRotacion from './PanelRotacion';
import { BarraConsumo, ChipDesvio } from './Semaforo';
import VistaDiaria from './VistaDiaria';

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
        : 'border-l-4 border-l-transparent bg-white';
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
  const [modo, setModo] = useState<Modo>('mes');
  const [mesElegido, setMes] = useState('');
  const [cliente, setCliente] = useState('');
  const [pais, setPais] = useState('');
  const [q, setQ] = useState('');
  const [abiertos, setAbiertos] = useState<Set<string>>(() => new Set(MARCAS.map((m) => m.id)));

  const meses = useMemo(() => [...new Set(met.datos.map((m) => m.mes))].sort().reverse(), [met.datos]);
  const mes = mesElegido || meses[0] || '';
  const delMes = useMemo(() => met.datos.filter((m) => m.mes === mes), [met.datos, mes]);
  const dias = Math.max(...delMes.map((m) => m.dias ?? 0), 0) || 1;
  const hasta = delMes.find((m) => m.hasta)?.hasta ?? null;
  const diasMes = mes ? diasDelMes(mes) : 30;

  const campanas: CampanaGasto[] = useMemo(() => {
    const porId = new Map(delMes.map((m) => [m.campanaId, m]));
    return camp.datos.map((c) => {
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
      };
    });
  }, [camp.datos, delMes]);

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
      <div className="flex flex-wrap items-end justify-between gap-3 rounded-card bg-white px-4 py-3 shadow-card">
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
            opciones={paises.map((p) => ({ id: p, label: p }))}
          />
          {meses.length > 1 && (
            <Select
              etiqueta="Período"
              ariaLabel="Mes"
              valor={mes}
              onChange={setMes}
              todo="Último mes"
              opciones={meses.map((m) => ({ id: m, label: mesCorto(m) }))}
            />
          )}
        </div>
        <p className="text-xs text-mc-grey">
          Datos del {fecha(delMes[0].desde)} al {fecha(hasta)} · {dias} de {diasMes} días · API de Google Ads
        </p>
      </div>

      <PanelRotacion r={resumen} clientes={arbol} mes={mes} dias={dias} diasMes={diasMes} />

      <section>
        <SeccionTitulo meta={modo === 'calendario' ? 'cada día contra el presupuesto diario' : 'clic en cada fila para abrirla'}>
          {modo === 'calendario' ? 'Día a día' : 'Detalle por cliente, país, campaña y grupo'}
        </SeccionTitulo>
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <div className="inline-flex overflow-hidden rounded-lg border border-mc-hair bg-white text-sm">
            {MODOS.map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => setModo(m)}
                className={`px-3 py-1.5 font-medium transition ${modo === m ? 'bg-mc-navy text-white' : 'text-mc-ink hover:bg-mc-tint'}`}
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
            className="min-w-[180px] flex-1 rounded-lg border border-mc-hair bg-white px-2.5 py-1.5 text-sm focus:border-mc-blue focus:outline-none"
          />
          {modo !== 'calendario' && (
            <button
              type="button"
              onClick={expandirTodo}
              className="rounded-lg border border-mc-hair bg-white px-3 py-1.5 text-sm text-mc-navy hover:bg-mc-tint"
            >
              Expandir todo
            </button>
          )}
        </div>

        {modo === 'calendario' ? (
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
            {metD.cargando ? <EsqueletoPresupuesto /> : <VistaDiaria campanas={visibles} dias={metD.datos} />}
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
              {modo === 'mes' && (
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
                  <span className="text-right">{modo === 'mes' ? `Presup. × ${diasMes} d` : 'Presup. / día'}</span>
                  <span className="text-right">{modo === 'mes' ? 'Gasto del mes' : 'Gasto / día'}</span>
                  <span>{modo === 'mes' ? 'Consumo del presupuesto (0–100%)' : 'Uso del presupuesto diario'}</span>
                  <span className="text-center">Desvío</span>
                  <span className="text-right">Clics</span>
                  <span className="text-right">Conv.</span>
                </div>
                {arbol.map((n) => (
                  <Fila key={n.clave} n={n} modo={modo} dias={dias} diasMes={diasMes} abiertos={abiertos} alternar={alternar} />
                ))}
              </div>
            </Tarjeta>
            <p className="mt-3 text-xs text-mc-grey">
              Presupuesto: el diario configurado en Google Ads, solo de campañas activas; en la vista mensual, × {diasMes} días. Consumo: gasto acumulado sobre
              el presupuesto del mes completo. El semáforo compara el gasto por día (sobre {dias} días con datos) contra el presupuesto por día. Los grupos de
              anuncios no tienen presupuesto propio.
            </p>
          </>
        )}
      </section>
    </div>
  );
}
