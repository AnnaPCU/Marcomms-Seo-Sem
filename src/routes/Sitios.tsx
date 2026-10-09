/**
 * Sitios: visitas, canales y contactos reales de cada sitio según Google Analytics 4, cruzados con los clics de
 * Google Ads. Una fila por sitio; al abrirla, alertas, canales y páginas de entrada pagas y orgánicas.
 */
import { useMemo, useState } from 'react';
import { AlertTriangle, ChevronRight, Info } from 'lucide-react';
import { useCampanas, useGa4, useMetricas } from '@/hooks/useDatos';
import type { Ga4Landing, Ga4SitioMes } from '@/services/ga4';
import { MARCAS } from '@/constants/estados';
import { ChipMarca, ErrorBox, Intro, Pildora, SeccionTitulo, Select, Tarjeta, Vacio } from '@/components/shared/Ui';
import { EsqueletoPresupuesto } from '@/components/shared/Loader';
import { alertas, canal, CANALES, clicsAds, esPaginaReal, MIN_LANDING, tasa, totales, tramosCanal, UMBRAL_LANDING, UMBRAL_MEDICION, type Alerta } from '@/utils/ga4';
import { entero, fecha, mesCorto, pct } from '@/utils/formato';
import { diasDelMes } from '@/utils/presupuesto';

const COLUMNAS = 'grid grid-cols-[20px_minmax(190px,1.3fr)_80px_minmax(130px,1fr)_minmax(170px,1.4fr)_120px_90px_92px] items-center gap-3';

function duracion(seg: number): string {
  const m = Math.floor(seg / 60);
  return m ? `${m} min ${Math.round(seg % 60)} s` : `${Math.round(seg)} s`;
}

/** Barra horizontal de proporción, gris de fondo. */
function Barra({ valor, color = 'bg-mc-blue' }: { valor: number; color?: string }) {
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full bg-mc-tint2">
      <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.min(100, Math.round(valor * 100))}%` }} />
    </div>
  );
}

function MezclaCanales({ s }: { s: Ga4SitioMes }) {
  const tramos = tramosCanal(s.datos);
  return (
    <div className="flex h-2.5 w-full overflow-hidden rounded-full bg-mc-tint2" title={tramos.map((t) => `${t.label}: ${entero(t.sesiones)}`).join(' · ')}>
      {tramos.map((t) => (
        <div key={t.id} className={t.color} style={{ width: `${tasa(t.sesiones, s.datos.sesiones) * 100}%` }} />
      ))}
    </div>
  );
}

function Medicion({ pagas, clics }: { pagas: number; clics: number | null }) {
  if (clics === null) return <span className="text-xs text-mc-grey">{pagas ? `${entero(pagas)} visitas` : 'sin Ads'}</span>;
  const r = tasa(pagas, clics);
  const mal = clics >= 30 && r < UMBRAL_MEDICION;
  return (
    <div className="text-xs">
      <div className="font-mono text-mc-navy">
        {entero(pagas)} <span className="text-mc-grey">de</span> {entero(clics)}
      </div>
      <div className={mal ? 'font-semibold text-red-700' : 'text-mc-grey'}>{clics ? `GA4 ve ${pct(pagas, clics)}` : 'sin clics'}</div>
    </div>
  );
}

function Landings({ titulo, lista, color }: { titulo: string; lista: Ga4Landing[]; color: string }) {
  const reales = lista.filter(esPaginaReal);
  return (
    <div>
      <div className="mb-1.5 text-[10px] font-bold uppercase tracking-[0.14em] text-mc-grey">{titulo}</div>
      {reales.length === 0 ? (
        <p className="text-xs text-mc-grey">Sin visitas en el período.</p>
      ) : (
        <ul className="space-y-1.5">
          {reales.map((l) => (
            <li key={l.pagina} className="text-xs">
              <div className="flex items-baseline justify-between gap-2">
                <span className="truncate text-mc-ink" title={l.pagina}>
                  {l.pagina}
                </span>
                <span className="shrink-0 font-mono text-mc-navy">
                  {entero(l.sesiones)} <span className="text-mc-grey">· {pct(l.interaccion, l.sesiones)}</span>
                </span>
              </div>
              <Barra valor={tasa(l.interaccion, l.sesiones)} color={l.sesiones >= MIN_LANDING && tasa(l.interaccion, l.sesiones) < UMBRAL_LANDING ? 'bg-mc-red' : color} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function Detalle({ s, avisos }: { s: Ga4SitioMes; avisos: Alerta[] }) {
  const d = s.datos;
  const contactos = Object.entries(d.contactos).sort((a, b) => b[1].formularios + b[1].emails - (a[1].formularios + a[1].emails));
  return (
    <div className="space-y-4 border-t border-mc-hair/70 bg-mc-tint/60 px-4 py-4 pl-10">
      {avisos.length > 0 && (
        <ul className="space-y-2">
          {avisos.map((a) => (
            <li key={a.clave} className={`rounded-lg border-l-[3px] bg-white px-3 py-2 text-xs shadow-card ${a.gravedad === 'alta' ? 'border-l-mc-red' : 'border-l-mc-gold'}`}>
              <div className="font-semibold text-mc-navy">{a.titulo}</div>
              <div className="mt-0.5 text-mc-ink">{a.detalle}</div>
            </li>
          ))}
        </ul>
      )}
      <div className="grid gap-5 md:grid-cols-3">
        <div>
          <div className="mb-1.5 text-[10px] font-bold uppercase tracking-[0.14em] text-mc-grey">Canales · visitas y % con interacción</div>
          <ul className="space-y-1.5">
            {tramosCanal(d).map((t) => (
              <li key={t.id} className="text-xs">
                <div className="flex items-baseline justify-between gap-2">
                  <span className="flex items-center gap-1.5 text-mc-ink">
                    <span className={`inline-block h-2 w-2 rounded-sm ${t.color}`} />
                    {t.label}
                  </span>
                  <span className="font-mono text-mc-navy">
                    {entero(t.sesiones)} <span className="text-mc-grey">· {pct(t.interaccion, t.sesiones)}</span>
                  </span>
                </div>
              </li>
            ))}
          </ul>
          <div className="mt-3 text-[10px] font-bold uppercase tracking-[0.14em] text-mc-grey">Contactos reales por canal</div>
          {contactos.length === 0 ? (
            <p className="mt-1 text-xs text-mc-grey">Ninguno medido en GA4.</p>
          ) : (
            <ul className="mt-1 space-y-0.5 text-xs">
              {contactos.map(([c, v]) => (
                <li key={c} className="flex justify-between text-mc-ink">
                  <span>{CANALES.find((x) => x.id === c)?.label ?? c}</span>
                  <span className="font-mono text-mc-navy">
                    {v.formularios ? `${v.formularios} form. · ` : ''}
                    {v.emails} email{v.emails === 1 ? '' : 's'}
                  </span>
                </li>
              ))}
            </ul>
          )}
          <p className="mt-3 text-[11px] text-mc-grey">
            {entero(d.usuarios)} usuarios · {entero(d.vistas)} páginas vistas · {duracion(d.duracion_media)} por visita
          </p>
        </div>
        <Landings titulo="Páginas de entrada desde Ads" lista={d.landings_pagas} color="bg-mc-blue" />
        <Landings titulo="Páginas de entrada desde Google orgánico" lista={d.landings_organicas} color="bg-mc-green" />
      </div>
    </div>
  );
}

function Fila({ s, clics, abierto, alternar }: { s: Ga4SitioMes; clics: number | null; abierto: boolean; alternar: () => void }) {
  const d = s.datos;
  const avisos = useMemo(() => alertas(d, clics), [d, clics]);
  const altas = avisos.filter((a) => a.gravedad === 'alta').length;
  return (
    <div className="border-t border-mc-hair/70 first:border-t-0">
      <button type="button" onClick={alternar} aria-expanded={abierto} className={`${COLUMNAS} w-full px-4 py-2.5 text-left text-[13px] transition hover:bg-mc-tint/70`}>
        <ChevronRight size={14} className={`text-mc-grey transition ${abierto ? 'rotate-90' : ''}`} />
        <span className="min-w-0">
          <span className="flex items-center gap-1.5 font-semibold text-mc-navy">
            <ChipMarca marca={s.marca} />
            <span className="truncate">{s.nombre.replace(/^(Control Union|Peterson Solutions)\s*/, '')}</span>
          </span>
          <span className="block truncate text-[11px] text-mc-grey">{s.sitio}</span>
        </span>
        <span className="text-right font-mono text-mc-navy">{entero(d.sesiones)}</span>
        <span>
          <span className="flex justify-between text-xs">
            <span className="font-mono text-mc-navy">{entero(d.interaccion)}</span>
            <span className="text-mc-grey">{pct(d.interaccion, d.sesiones)}</span>
          </span>
          <Barra valor={tasa(d.interaccion, d.sesiones)} />
        </span>
        <MezclaCanales s={s} />
        <Medicion pagas={canal(d, 'Paid Search').sesiones} clics={clics} />
        <span className="text-right">
          <span className="font-mono font-semibold text-mc-navy">{d.contactos_total}</span>
          <span className="block text-[11px] text-mc-grey">{d.contactos_total ? `1 cada ${entero(d.interaccion / d.contactos_total)}` : 'sin medir'}</span>
        </span>
        <span className="text-center">
          {avisos.length ? (
            <Pildora tono={altas ? 'rojo' : 'dorado'}>
              <AlertTriangle size={11} /> {avisos.length}
            </Pildora>
          ) : (
            <Pildora tono="verde">OK</Pildora>
          )}
        </span>
      </button>
      {abierto && <Detalle s={s} avisos={avisos} />}
    </div>
  );
}

export default function Sitios() {
  const ga4 = useGa4();
  const camp = useCampanas();
  const met = useMetricas();
  const [cliente, setCliente] = useState('');
  const [mesElegido, setMes] = useState('');
  const [abiertos, setAbiertos] = useState<Set<string>>(new Set());

  const meses = useMemo(() => {
    const m = new Map<string, Ga4SitioMes>();
    ga4.datos.forEach((s) => m.set(s.mes, s));
    return [...m.values()].sort((a, b) => b.mes.localeCompare(a.mes)).map((s) => ({ mes: s.mes, dias: s.dias, hasta: s.hasta }));
  }, [ga4.datos]);
  // Por defecto, el último mes completo: el mes en curso tiene pocos días y todavía no tiene el gasto de Ads cruzado.
  const porDefecto = meses.find((m) => m.dias === diasDelMes(m.mes))?.mes ?? meses[0]?.mes ?? '';
  const mes = mesElegido || porDefecto;

  const filas = useMemo(
    () =>
      ga4.datos
        .filter((s) => s.mes === mes && (!cliente || s.marca === cliente))
        .map((s) => ({ s, clics: clicsAds(s.sitio, s.mes, camp.datos, met.datos) }))
        .sort((a, b) => b.s.datos.interaccion - a.s.datos.interaccion),
    [ga4.datos, mes, cliente, camp.datos, met.datos],
  );
  const t = totales(filas.map((f) => f.s.datos));
  const conAlerta = filas.filter((f) => alertas(f.s.datos, f.clics).length).length;
  const ref = filas[0]?.s;

  const alternar = (k: string) =>
    setAbiertos((prev) => {
      const n = new Set(prev);
      if (n.has(k)) n.delete(k);
      else n.add(k);
      return n;
    });

  const error = ga4.error || camp.error || met.error;
  if (error) return <ErrorBox mensaje={error} />;
  if (ga4.cargando) return <EsqueletoPresupuesto />;
  if (!ga4.datos.length) return <Vacio>Todavía no hay datos de GA4. Corré ga4_export.py y después scripts/publicar.py --solo ga4.</Vacio>;

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex flex-wrap items-end justify-between gap-3 rounded-card bg-white px-4 py-3 shadow-card">
        <div className="flex flex-wrap items-end gap-3">
          <Select
            etiqueta="Cliente"
            ariaLabel="Cliente"
            valor={cliente}
            onChange={setCliente}
            todo="Todos los clientes"
            opciones={MARCAS.filter((m) => m.id !== 'PCU').map((m) => ({ id: m.id, label: m.label }))}
          />
          <Select
            etiqueta="Período"
            ariaLabel="Mes"
            valor={mesElegido}
            onChange={setMes}
            todo={`${mesCorto(porDefecto)} (último completo)`}
            opciones={meses.filter((m) => m.mes !== porDefecto).map((m) => ({ id: m.mes, label: m.dias === diasDelMes(m.mes) ? mesCorto(m.mes) : `${mesCorto(m.mes)} (al ${fecha(m.hasta)})` }))}
          />
        </div>
        {ref && (
          <p className="text-xs text-mc-grey">
            Datos del {fecha(ref.desde)} al {fecha(ref.hasta)} · {ref.dias} días · Google Analytics 4
          </p>
        )}
      </div>

      <Intro
        cifras={[
          { valor: entero(t.interaccion), etiqueta: 'visitas reales' },
          { valor: pct(t.organico, t.sesiones), etiqueta: 'orgánico' },
          { valor: entero(t.contactos), etiqueta: 'contactos', tono: 'text-emerald-700' },
          { valor: conAlerta, etiqueta: 'con alertas', tono: conAlerta ? 'text-red-700' : 'text-mc-navy' },
        ]}
      >
        Visitas reales = sesiones con interacción ({pct(t.interaccion, t.sesiones)} de {entero(t.sesiones)}): descuenta rebotes y bots. Contactos =
        formularios del sitio y clics a un email comercial; no cuenta el buscador, el acceso de administración ni los emails de empleo.
      </Intro>

      <section>
        <SeccionTitulo meta="clic en un sitio para ver canales, páginas y alertas">Sitios ordenados por visitas reales</SeccionTitulo>
        <div className="mb-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-mc-grey">
          {CANALES.map((c) => (
            <span key={c.id} className="flex items-center gap-1.5">
              <span className={`inline-block h-2 w-2 rounded-sm ${c.color}`} />
              {c.label}
            </span>
          ))}
          <span className="flex items-center gap-1.5">
            <span className="inline-block h-2 w-2 rounded-sm bg-mc-hair" />
            Otros
          </span>
        </div>
        {filas.length === 0 ? (
          <Vacio>No hay sitios de este cliente en el período.</Vacio>
        ) : (
          <Tarjeta className="overflow-x-auto">
            <div className="min-w-[960px]">
              <div className={`${COLUMNAS} px-4 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-mc-grey`}>
                <span />
                <span>Sitio</span>
                <span className="text-right">Sesiones</span>
                <span>Con interacción</span>
                <span>De dónde llegan</span>
                <span>Pago: GA4 / clics Ads</span>
                <span className="text-right">Contactos</span>
                <span className="text-center">Alertas</span>
              </div>
              {filas.map(({ s, clics }) => (
                <Fila key={s.sitio} s={s} clics={clics} abierto={abiertos.has(s.sitio)} alternar={() => alternar(s.sitio)} />
              ))}
            </div>
          </Tarjeta>
        )}
      </section>

      <div className="flex gap-2 rounded-card border border-mc-hair/70 bg-white px-4 py-3 text-xs leading-relaxed text-mc-ink shadow-card">
        <Info size={15} className="mt-0.5 shrink-0 text-mc-blue" />
        <p>
          <b className="text-mc-navy">Cómo leer estos números.</b> GA4 solo mide a quien acepta las cookies: en España y Portugal ve bastante menos visitas
          pagas que los clics que cobra Ads (columna «Pago»), y lo mismo pasa con el orgánico frente a Search Console. Los formularios de HubSpot
          embebidos no llegan a GA4, así que los contactos de esos sitios están subestimados; los de Peterson Solutions hoy no se miden. Las propiedades
          de GA4 no están vinculadas a Google Ads: las conversiones de Ads no salen de acá.
        </p>
      </div>
    </div>
  );
}
