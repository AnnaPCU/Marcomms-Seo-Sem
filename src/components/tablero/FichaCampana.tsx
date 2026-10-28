/**
 * Ficha «campaña»: una sola tarjeta con todo lo que hay que hacer en una campaña (una acción no se reparte en varias
 * tarjetas). Dice dónde (campaña, grupo y anuncio con su id), por qué, los pasos en orden, las keywords y negativas
 * con su motivo, y para cada anuncio los títulos y descripciones propuestos con su motivo, con las prioritarias
 * destacadas. Los datos vienen en `evidencia` (ficha: 'campana').
 */
import { useState, type ReactNode } from 'react';
import { Check, CheckCircle2, Copy, MapPin, Star } from 'lucide-react';
import { ACCION_BY_ID } from '@/constants/estados';
import { ars, entero } from '@/utils/formato';
import IconoAccion from './IconoAccion';
import { Ayuda, BloqueOrganico, ChipRelacion, Rotulo, type OrganicoFicha, type TerminoFicha } from './Fichas';

export interface Propuesta {
  texto: string;
  motivo?: string;
  /** Las que de verdad conviene hacer: se destacan. */
  prioritario?: boolean;
  /** Título o descripción actual al que reemplaza. */
  reemplaza?: string;
}
export interface Quitar {
  texto: string;
  motivo?: string;
}
export interface AnuncioCampana {
  grupo: string;
  anuncio_id?: string;
  /** Cómo reconocerlo en Google Ads: «RSA de fuerza Pobre, 37 clics». */
  anuncio_desc?: string;
  accion?: string; // 'Ajustar' | 'Reescribir' | 'Anuncio nuevo'
  motivo?: string;
  url?: string;
  gasto_ars?: number;
  clics?: number;
  ventanas?: string;
  titulos_hoy?: string[];
  descripciones_hoy?: string[];
  quitar?: (Quitar | string)[];
  titulos_propuestos?: (Propuesta | string)[];
  descripciones_propuestas?: (Propuesta | string)[];
  terminos?: TerminoFicha[];
  nota?: string;
}
export interface KeywordPropuesta {
  texto: string;
  concordancia: string; // 'exacta' | 'frase' | 'amplia'
  grupo?: string;
  accion?: string; // 'agregar' | 'pausar' | 'cambiar a exacta'…
  motivo?: string;
}
export interface NegativaPropuesta {
  texto: string;
  concordancia: string;
  nivel: string; // 'campaña' | 'grupo'
  grupo?: string;
  motivo?: string;
}
/** Una cosa concreta para cargar o cambiar: una negativa, una keyword, un título, una redirección… */
export interface ItemPaso {
  accion: string; // 'agregar' | 'pausar' | 'quitar' | 'reemplazar' | 'cambiar' | 'crear' | 'decidir' | 'redirigir' | 'editar'
  tipo: string; // 'negativa' | 'keyword' | 'titulo' | 'descripcion' | 'grupo' | 'url' | 'title' | 'meta' | 'h1' | 'texto'
  texto: string;
  concordancia?: string; // 'exacta' | 'frase' | 'amplia' (negativas y keywords)
  destino: string; // 'Toda la campaña', 'Grupo «X»', 'Anuncio id N', una URL…
  reemplaza?: string;
  prioritario?: boolean;
  opcional?: boolean;
  motivo?: string;
}
export interface Paso {
  accion: string; // id de ACCIONES
  titulo: string;
  donde?: string;
  detalle?: string;
  items?: ItemPaso[];
  hecho?: boolean;
}
export interface PaginaSeo {
  url: string;
  nota?: string;
}
export interface DatosCampana {
  ficha: 'campana' | 'seo';
  unidad?: string;
  campana?: string;
  campanas?: string[];
  sitio?: string;
  paginas?: PaginaSeo[];
  resumen?: string;
  por_que?: string;
  ya_hecho?: string;
  pasos?: Paso[];
  keywords?: KeywordPropuesta[];
  negativas?: NegativaPropuesta[];
  negativas_decision?: string;
  anuncios?: AnuncioCampana[];
  organico?: OrganicoFicha[];
  organico_desde?: string | null;
  organico_hasta?: string;
  datos_hasta?: string;
}

/** Cómo se escribe en Google Ads: [exacta], "frase", amplia. */
export function notacion(texto: string, concordancia?: string): string {
  return concordancia === 'exacta' ? `[${texto}]` : concordancia === 'frase' ? `"${texto}"` : texto;
}

const VERBO: Record<string, string> = {
  agregar: 'Agregar',
  pausar: 'Pausar',
  quitar: 'Quitar',
  reemplazar: 'Reemplazar',
  cambiar: 'Cambiar',
  crear: 'Crear',
  decidir: 'Decidir',
  redirigir: 'Redirigir',
  editar: 'Editar',
};
const TIPO_ITEM: Record<string, string> = {
  negativa: 'negativa',
  keyword: 'keyword',
  titulo: 'título',
  descripcion: 'descripción',
  grupo: 'grupo',
  url: 'URL',
  title: 'title',
  meta: 'meta description',
  h1: 'H1',
  texto: '',
};
/** Dónde se hace cada tipo de paso. */
const COMO: Record<string, string> = {
  negativas:
    'En Google Ads: la campaña › Palabras clave › Palabras clave negativas › +. Elegí «campaña» o «grupo de anuncios» según el destino de cada bloque y pegá las líneas tal cual (los corchetes y comillas marcan la concordancia).',
  keywords: 'En Google Ads: la campaña › el grupo › Palabras clave › +. Pegá las líneas tal cual: [exacta], "frase", amplia sin signos.',
  pausa: 'En Google Ads: la campaña › el grupo › Palabras clave › tildá la keyword › Editar › Pausar.',
  anuncio: 'En Google Ads: la campaña › el grupo › Anuncios › el anuncio con ese id › Editar. Cambiar los recursos uno por uno.',
  estructura: 'En Google Ads: la campaña › Grupos de anuncios › + › nombre del grupo, URL final, keywords y anuncio de este paso.',
};

const prop = (p: Propuesta | string): Propuesta => (typeof p === 'string' ? { texto: p } : p);

function Copiar({ texto }: { texto: string }) {
  const [ok, setOk] = useState(false);
  return (
    <button
      type="button"
      onClick={() => {
        void navigator.clipboard?.writeText(texto).then(() => {
          setOk(true);
          window.setTimeout(() => setOk(false), 1500);
        });
      }}
      className="inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[11px] font-semibold text-mc-blue hover:bg-mc-tint"
    >
      {ok ? <Check size={12} /> : <Copy size={12} />}
      {ok ? 'Copiado' : 'Copiar'}
    </button>
  );
}

/** La lista exacta de lo que hay que cargar en un paso, agrupada por destino. */
function ItemsPaso({ items }: { items: ItemPaso[] }) {
  const destinos = [...new Set(items.map((i) => i.destino))];
  return (
    <div className="mt-2 space-y-2">
      {destinos.map((dest) => {
        const lista = items.filter((i) => i.destino === dest);
        const pegables = lista.filter((i) => (i.tipo === 'negativa' || i.tipo === 'keyword') && i.accion === 'agregar');
        return (
          <div key={dest} className="rounded-lg bg-mc-tint px-3 py-2">
            <div className="mb-1 flex items-center justify-between gap-2">
              <span className="text-[11.5px] font-semibold text-mc-navy">{dest}</span>
              {pegables.length > 1 && <Copiar texto={pegables.map((i) => notacion(i.texto, i.concordancia)).join('\n')} />}
            </div>
            <ul className="space-y-1">
              {lista.map((i, k) => (
                <li key={k} className={`text-[13px] leading-snug ${i.opcional ? 'opacity-75' : ''}`}>
                  <span className="mr-1.5 inline-block min-w-[74px] text-[11px] font-semibold uppercase tracking-[0.06em] text-mc-grey">
                    {VERBO[i.accion] ?? i.accion}
                    {TIPO_ITEM[i.tipo] ? ` ${TIPO_ITEM[i.tipo]}` : ''}
                  </span>
                  {i.prioritario && <Star size={11} className="mr-1 inline -translate-y-px fill-mc-gold text-mc-gold" />}
                  {i.reemplaza && (
                    <>
                      <span className="text-red-800 line-through decoration-red-300">{i.reemplaza}</span>
                      <span className="mx-1 text-mc-grey">→</span>
                    </>
                  )}
                  <span className={`font-mono text-[12.5px] ${i.tipo === 'negativa' ? 'text-red-700' : 'text-mc-navy'} ${i.prioritario ? 'font-bold' : ''}`}>
                    {i.tipo === 'negativa' || i.tipo === 'keyword' ? notacion(i.texto, i.concordancia) : i.texto}
                  </span>
                  {i.opcional && <span className="ml-1.5 text-[11px] text-mc-grey">(opcional)</span>}
                  {i.motivo && <span className="ml-2 text-[12px] text-mc-ink">{i.motivo}</span>}
                </li>
              ))}
            </ul>
          </div>
        );
      })}
    </div>
  );
}
const qt = (q: Quitar | string): Quitar => (typeof q === 'string' ? { texto: q } : q);

function Caja({ titulo, children, tono = 'neutro' }: { titulo: ReactNode; children: ReactNode; tono?: 'neutro' | 'rojo' | 'verde' }) {
  const borde = tono === 'rojo' ? 'border-l-mc-red' : tono === 'verde' ? 'border-l-mc-green' : 'border-l-mc-blue';
  return (
    <div className={`rounded-card border border-l-4 border-mc-hair/70 ${borde} bg-mc-sup px-4 py-3`}>
      <Rotulo>{titulo}</Rotulo>
      {children}
    </div>
  );
}

function ListaPropuestas({ items, limite }: { items: (Propuesta | string)[]; limite: number }) {
  const lista = items.map(prop);
  const hayPrioritarias = lista.some((p) => p.prioritario);
  // primero las prioritarias, sin cambiar el orden dentro de cada grupo
  const orden = [...lista.filter((p) => p.prioritario), ...lista.filter((p) => !p.prioritario)];
  return (
    <ul className="space-y-1">
      {orden.map((p) => (
        <li
          key={p.texto}
          className={`rounded-lg px-2.5 py-1.5 ${p.prioritario ? 'bg-amber-50 ring-1 ring-amber-200' : hayPrioritarias ? 'opacity-80' : ''}`}
        >
          <div className="flex items-start justify-between gap-3 text-[13.5px] text-mc-navy">
            <span className={p.prioritario ? 'font-semibold' : ''}>
              {p.prioritario && <Star size={12} className="mr-1 inline -translate-y-px fill-mc-gold text-mc-gold" />}
              {p.texto}
            </span>
            <span className={`shrink-0 font-mono text-[11px] ${p.texto.length > limite ? 'font-bold text-red-700' : 'text-mc-grey'}`}>
              {p.texto.length}/{limite}
            </span>
          </div>
          {(p.motivo || p.reemplaza) && (
            <p className="mt-0.5 text-[12px] leading-snug text-mc-ink">
              {p.reemplaza && (
                <span className="mr-1 text-mc-grey">
                  Reemplaza «<span className="line-through decoration-red-300">{p.reemplaza}</span>».
                </span>
              )}
              {p.motivo}
            </p>
          )}
        </li>
      ))}
    </ul>
  );
}

function BloqueAnuncio({ a }: { a: AnuncioCampana }) {
  return (
    <div className="space-y-4 rounded-card border border-mc-hair/70 p-4">
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-[13px]">
        <span className="font-semibold text-mc-navy">Grupo «{a.grupo}»</span>
        <span className="text-mc-hair">·</span>
        <span className="text-mc-ink">
          {a.anuncio_id ? <>anuncio id <b className="font-mono text-mc-navy">{a.anuncio_id}</b></> : 'anuncio nuevo'}
          {a.anuncio_desc ? ` · ${a.anuncio_desc}` : ''}
        </span>
        {a.accion && <span className="ml-auto rounded bg-mc-fuerte px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.12em] text-white">{a.accion}</span>}
      </div>
      {(a.gasto_ars !== undefined || a.ventanas) && (
        <p className="-mt-2 text-[12px] text-mc-grey">
          {a.gasto_ars !== undefined && <>{ars(a.gasto_ars)}{a.clics !== undefined ? ` · ${entero(a.clics)} clics` : ''} </>}
          {a.ventanas && <>({a.ventanas})</>}
          {a.url && (
            <>
              {' '}· URL <span className="break-all text-mc-ink">{a.url}</span>
            </>
          )}
        </p>
      )}
      {a.motivo && (
        <div className="rounded-lg bg-mc-tint px-3 py-2">
          <Rotulo>Por qué cambiar este anuncio</Rotulo>
          <p className="text-[13.5px] leading-relaxed text-mc-navy">{a.motivo}</p>
        </div>
      )}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <div className="space-y-4">
          {!!a.titulos_hoy?.length && (
            <section>
              <Rotulo>Qué dice hoy</Rotulo>
              <p className="text-[13px] leading-relaxed text-mc-ink">{a.titulos_hoy.join(' | ')}</p>
              {!!a.descripciones_hoy?.length && <p className="mt-1.5 text-[12.5px] leading-relaxed text-mc-grey">{a.descripciones_hoy.join(' | ')}</p>}
            </section>
          )}
          {!!a.quitar?.length && (
            <section>
              <Rotulo>Quitar</Rotulo>
              <ul className="space-y-1">
                {a.quitar.map(qt).map((q) => (
                  <li key={q.texto} className="text-[12.5px]">
                    <span className="rounded-md bg-red-50 px-2 py-0.5 text-red-800 line-through decoration-red-300 ring-1 ring-red-100">{q.texto}</span>
                    {q.motivo && <span className="ml-2 text-mc-ink">{q.motivo}</span>}
                  </li>
                ))}
              </ul>
            </section>
          )}
          {!!a.terminos?.length && (
            <section>
              <Rotulo>Qué buscó la gente que lo activó</Rotulo>
              <ul className="divide-y divide-mc-tint2 text-[13px]">
                {a.terminos.map((t) => (
                  <li key={t.termino} className="flex items-center gap-2 py-1.5">
                    <span className="min-w-0 flex-1 truncate text-mc-navy" title={t.termino}>
                      {t.termino}
                    </span>
                    {t.relacion && <ChipRelacion relacion={t.relacion} />}
                    <span className="w-28 text-right font-mono text-[12px] text-mc-ink">
                      {ars(t.coste)}
                      {t.clics !== undefined ? ` · ${t.clics}` : ''}
                    </span>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
        <div className="space-y-4 rounded-card bg-mc-tint px-4 py-3">
          <section>
            <Rotulo>Títulos propuestos</Rotulo>
            <ListaPropuestas items={a.titulos_propuestos ?? []} limite={30} />
          </section>
          <section>
            <Rotulo>Descripciones propuestas</Rotulo>
            <ListaPropuestas items={a.descripciones_propuestas ?? []} limite={90} />
          </section>
          {a.nota && <p className="border-t border-mc-hair/70 pt-2 text-[12.5px] leading-relaxed text-mc-grey">{a.nota}</p>}
        </div>
      </div>
      {[...(a.titulos_propuestos ?? []), ...(a.descripciones_propuestas ?? [])].map(prop).some((p) => p.prioritario) && (
        <p className="flex items-center gap-1.5 text-[11.5px] text-mc-grey">
          <Star size={12} className="fill-mc-gold text-mc-gold" /> Destacadas: las que conviene cargar sí o sí. El resto suma variantes para que Google
          combine, pero no cambian el resultado por sí solas.
        </p>
      )}
    </div>
  );
}

export function FichaCampana({ d }: { d: DatosCampana }) {
  const campanas = d.campanas?.length ? d.campanas : d.campana ? [d.campana] : [];
  const grupos = [...new Set([...(d.anuncios ?? []).map((a) => a.grupo), ...(d.keywords ?? []).map((k) => k.grupo).filter(Boolean)])] as string[];
  return (
    <div className="space-y-5">
      <div className="rounded-card bg-mc-tint px-4 py-3">
        <Rotulo>
          <MapPin size={11} className="mr-1 inline -translate-y-px" />
          Dónde
        </Rotulo>
        <dl className="grid grid-cols-[90px_1fr] gap-x-3 gap-y-1 text-[13px]">
          {d.ficha === 'seo' ? (
            <>
              <dt className="text-mc-grey">Sitio</dt>
              <dd className="font-semibold text-mc-navy">{d.sitio ?? '—'}</dd>
              {!!d.paginas?.length && (
                <>
                  <dt className="text-mc-grey">{d.paginas.length > 1 ? 'Páginas' : 'Página'}</dt>
                  <dd className="space-y-0.5 text-mc-navy">
                    {d.paginas.map((p) => (
                      <div key={p.url}>
                        <span className="break-all font-mono text-[12px]">{p.url}</span>
                        {p.nota && <span className="ml-2 text-[12px] text-mc-grey">{p.nota}</span>}
                      </div>
                    ))}
                  </dd>
                </>
              )}
            </>
          ) : (
            <>
              <dt className="text-mc-grey">{campanas.length > 1 ? 'Campañas' : 'Campaña'}</dt>
              <dd className="font-semibold text-mc-navy">{campanas.length ? campanas.join(' · ') : '—'}</dd>
            </>
          )}
          {grupos.length > 0 && (
            <>
              <dt className="text-mc-grey">{grupos.length > 1 ? 'Grupos' : 'Grupo'}</dt>
              <dd className="text-mc-navy">{grupos.join(' · ')}</dd>
            </>
          )}
          {(d.anuncios ?? []).some((a) => a.anuncio_id) && (
            <>
              <dt className="text-mc-grey">Anuncios</dt>
              <dd className="text-mc-navy">
                {(d.anuncios ?? [])
                  .filter((a) => a.anuncio_id)
                  .map((a) => `«${a.grupo}»: id ${a.anuncio_id}${a.anuncio_desc ? ` (${a.anuncio_desc})` : ''}`)
                  .join(' · ')}
              </dd>
            </>
          )}
        </dl>
      </div>

      {(d.por_que || d.ya_hecho) && (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {d.por_que && (
            <Caja titulo="Por qué" tono="rojo">
              <p className="text-[13.5px] leading-relaxed text-mc-navy">{d.por_que}</p>
            </Caja>
          )}
          {d.ya_hecho && (
            <Caja titulo="Lo que ya está hecho" tono="verde">
              <p className="text-[13.5px] leading-relaxed text-mc-navy">{d.ya_hecho}</p>
            </Caja>
          )}
        </div>
      )}

      {!!d.pasos?.length && (
        <section>
          <Rotulo>Qué hacer, en orden</Rotulo>
          <ol className="space-y-2">
            {d.pasos.map((p, i) => (
              <li key={i} className={`flex gap-3 rounded-lg border border-mc-hair/70 px-3 py-2 ${p.hecho ? 'opacity-60' : ''}`}>
                <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-mc-fuerte font-mono text-[11px] font-bold text-white">{i + 1}</span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-x-2 text-[13.5px] font-semibold text-mc-navy">
                    <IconoAccion id={p.accion} size={13} />
                    {p.titulo}
                    <span className="text-[11px] font-normal text-mc-grey">{ACCION_BY_ID[p.accion]?.corto}</span>
                    {p.hecho && (
                      <span className="inline-flex items-center gap-1 text-[11px] font-normal text-emerald-700">
                        <CheckCircle2 size={12} /> hecho
                      </span>
                    )}
                  </div>
                  {p.donde && <div className="text-[12px] text-mc-grey">{p.donde}</div>}
                  {p.detalle && <p className="mt-0.5 whitespace-pre-line text-[13px] leading-relaxed text-mc-ink">{p.detalle}</p>}
                  {!!p.items?.length && <ItemsPaso items={p.items} />}
                  {!!p.items?.length && COMO[p.accion] && <p className="mt-1.5 text-[11.5px] leading-snug text-mc-grey">{COMO[p.accion]}</p>}
                </div>
              </li>
            ))}
          </ol>
        </section>
      )}

      {!!d.keywords?.length && (
        <section>
          <Rotulo>Keywords</Rotulo>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[560px] text-[13px]">
              <thead>
                <tr className="text-left text-[10px] uppercase tracking-[0.12em] text-mc-grey">
                  <th className="py-1 pr-2 font-semibold">Keyword</th>
                  <th className="py-1 pr-2 font-semibold">Concordancia</th>
                  <th className="py-1 pr-2 font-semibold">Grupo</th>
                  <th className="py-1 pr-2 font-semibold">Acción</th>
                  <th className="py-1 font-semibold">Por qué</th>
                </tr>
              </thead>
              <tbody>
                {d.keywords.map((k) => (
                  <tr key={`${k.texto}|${k.grupo}|${k.accion}`} className="border-t border-mc-tint2 align-top">
                    <td className="py-1.5 pr-2 font-mono text-[12.5px] text-mc-navy">{notacion(k.texto, k.concordancia)}</td>
                    <td className="py-1.5 pr-2 text-mc-ink">{k.concordancia}</td>
                    <td className="py-1.5 pr-2 text-mc-ink">{k.grupo ?? '—'}</td>
                    <td className="py-1.5 pr-2 font-semibold text-mc-navy">{k.accion ?? 'agregar'}</td>
                    <td className="py-1.5 text-mc-ink">{k.motivo}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {(d.negativas?.length || d.negativas_decision) && (
        <section>
          <Rotulo>Negativas</Rotulo>
          {d.negativas_decision && <p className="mb-2 text-[13.5px] leading-relaxed text-mc-navy">{d.negativas_decision}</p>}
          {!!d.negativas?.length && (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[560px] text-[13px]">
                <thead>
                  <tr className="text-left text-[10px] uppercase tracking-[0.12em] text-mc-grey">
                    <th className="py-1 pr-2 font-semibold">Negativa</th>
                    <th className="py-1 pr-2 font-semibold">Concordancia</th>
                    <th className="py-1 pr-2 font-semibold">Dónde</th>
                    <th className="py-1 font-semibold">Por qué</th>
                  </tr>
                </thead>
                <tbody>
                  {d.negativas.map((n) => (
                    <tr key={`${n.texto}|${n.nivel}|${n.grupo}`} className="border-t border-mc-tint2 align-top">
                      <td className="py-1.5 pr-2 font-mono text-[12.5px] text-red-700">−{notacion(n.texto, n.concordancia)}</td>
                      <td className="py-1.5 pr-2 text-mc-ink">{n.concordancia}</td>
                      <td className="py-1.5 pr-2 text-mc-ink">{n.nivel === 'grupo' ? `grupo «${n.grupo}»` : 'toda la campaña'}</td>
                      <td className="py-1.5 text-mc-ink">{n.motivo}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {(d.anuncios ?? []).map((a) => (
        <BloqueAnuncio key={`${a.grupo}|${a.anuncio_id}`} a={a} />
      ))}

      {d.organico && <BloqueOrganico organico={d.organico} desde={d.organico_desde ?? d.unidad} hasta={d.organico_hasta} />}
      {d.datos_hasta && (
        <Ayuda>
          Revisado contra la cuenta de Google Ads al {d.datos_hasta}: estructura (grupos, keywords, negativas y anuncios vigentes) y términos de búsqueda.
        </Ayuda>
      )}
    </div>
  );
}
