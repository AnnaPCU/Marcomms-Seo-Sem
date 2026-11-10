/**
 * Ficha «campaña» (SEM) y «seo»: al grano. Dónde se hace el cambio, cuál es el problema, qué se propone y qué hacer,
 * en orden, con la lista exacta de lo que hay que cargar en cada paso. El motivo de cada línea queda a un clic y los
 * datos que respaldan la propuesta (por qué, lo ya hecho, orgánico), plegados al final. Los datos vienen en
 * `evidencia` (ficha: 'campana' | 'seo'); keywords, negativas y anuncios completos siguen en la evidencia para el
 * Excel, pero no se repiten acá: los pasos ya dicen qué cargar.
 */
import { useState, type ReactNode } from 'react';
import { Check, CheckCircle2, Copy, MapPin, Star } from 'lucide-react';
import { ACCION_BY_ID } from '@/constants/estados';
import IconoAccion from './IconoAccion';
import { Ayuda, BloqueOrganico, Rotulo, type OrganicoFicha, type TerminoFicha } from './Fichas';

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
function ItemsPaso({ items, verMotivos }: { items: ItemPaso[]; verMotivos: boolean }) {
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
                  {verMotivos && i.motivo && <span className="ml-2 text-[12px] text-mc-grey">{i.motivo}</span>}
                </li>
              ))}
            </ul>
          </div>
        );
      })}
    </div>
  );
}

function Caja({ titulo, children, tono }: { titulo: ReactNode; children: ReactNode; tono: 'rojo' | 'verde' }) {
  return (
    <div className={`rounded-card border border-l-4 border-mc-hair/70 ${tono === 'rojo' ? 'border-l-mc-red' : 'border-l-mc-green'} bg-mc-sup px-4 py-3`}>
      <Rotulo>{titulo}</Rotulo>
      <div className="text-[13.5px] leading-relaxed text-mc-navy">{children}</div>
    </div>
  );
}

export function FichaCampana({ d, problema }: { d: DatosCampana; problema?: string }) {
  const [verMotivos, setVerMotivos] = useState(false);
  const campanas = d.campanas?.length ? d.campanas : d.campana ? [d.campana] : [];
  const grupos = [...new Set([...(d.anuncios ?? []).map((a) => a.grupo), ...(d.keywords ?? []).map((k) => k.grupo).filter(Boolean)])] as string[];
  const anuncios = (d.anuncios ?? []).filter((a) => a.anuncio_id);
  const hayMotivos = (d.pasos ?? []).some((p) => p.items?.some((i) => i.motivo));
  const hayRespaldo = !!(d.por_que || d.ya_hecho || d.organico?.length);
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
                      <div key={p.url} className="break-all font-mono text-[12px]">
                        {p.url}
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
          {anuncios.length > 0 && (
            <>
              <dt className="text-mc-grey">{anuncios.length > 1 ? 'Anuncios' : 'Anuncio'}</dt>
              <dd className="text-mc-navy">{anuncios.map((a) => `id ${a.anuncio_id} («${a.grupo}»)`).join(' · ')}</dd>
            </>
          )}
        </dl>
      </div>

      {(problema || d.resumen) && (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {problema && (
            <Caja titulo="El problema" tono="rojo">
              {problema}
            </Caja>
          )}
          {d.resumen && (
            <Caja titulo="La solución" tono="verde">
              {d.resumen}
            </Caja>
          )}
        </div>
      )}

      {!!d.pasos?.length && (
        <section>
          <div className="flex items-center justify-between gap-2">
            <Rotulo>Qué hacer, en orden</Rotulo>
            {hayMotivos && (
              <button type="button" onClick={() => setVerMotivos((v) => !v)} className="mb-1.5 text-[11.5px] font-semibold text-mc-blue hover:underline">
                {verMotivos ? 'Ocultar el motivo de cada línea' : 'Ver el motivo de cada línea'}
              </button>
            )}
          </div>
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
                  {!!p.items?.length && <ItemsPaso items={p.items} verMotivos={verMotivos} />}
                  {!!p.items?.length && COMO[p.accion] && <p className="mt-1.5 text-[11.5px] leading-snug text-mc-grey">{COMO[p.accion]}</p>}
                </div>
              </li>
            ))}
          </ol>
        </section>
      )}

      {hayRespaldo && (
        <details className="rounded-card border border-mc-hair/70 px-4 py-2 text-[13px]">
          <summary className="cursor-pointer select-none text-[12px] font-semibold text-mc-grey">Datos que respaldan la propuesta</summary>
          <div className="mt-2 space-y-3 text-mc-ink">
            {d.por_que && <p className="leading-relaxed">{d.por_que}</p>}
            {d.ya_hecho && (
              <p className="leading-relaxed">
                <span className="font-semibold text-mc-navy">Ya hecho: </span>
                {d.ya_hecho}
              </p>
            )}
            {d.organico && <BloqueOrganico organico={d.organico} desde={d.organico_desde ?? d.unidad} hasta={d.organico_hasta} />}
          </div>
        </details>
      )}
      {d.datos_hasta && <Ayuda>Datos al {d.datos_hasta}.</Ayuda>}
    </div>
  );
}
