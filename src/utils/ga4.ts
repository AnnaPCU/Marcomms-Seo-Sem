/**
 * Lectura de GA4 para la pestaña «Sitios»: canales, cruce con los clics de Google Ads y alertas. Sin dependencias de
 * React; se testea en ga4.test.ts.
 */
import type { Marca } from '@/lib/database.types';
import type { Ga4Datos, Ga4Landing } from '@/services/ga4';

/** Canales de GA4 (sessionDefaultChannelGroup) en el orden y con el nombre que se muestran. */
export const CANALES: { id: string; label: string; color: string }[] = [
  { id: 'Organic Search', label: 'Orgánico', color: 'bg-mc-green' },
  { id: 'Paid Search', label: 'Pago (Ads)', color: 'bg-mc-blue' },
  { id: 'Direct', label: 'Directo', color: 'bg-mc-grey' },
  { id: 'Referral', label: 'Referencias', color: 'bg-mc-gold' },
  { id: 'AI Assistant', label: 'Asistentes IA', color: 'bg-mc-indigo' },
  { id: 'Organic Social', label: 'Redes', color: 'bg-sky-300' },
  { id: 'Email', label: 'Email', color: 'bg-emerald-300' },
];
const OTROS = { id: 'otros', label: 'Otros', color: 'bg-mc-hair' };

export interface Tramo {
  id: string;
  label: string;
  color: string;
  sesiones: number;
  interaccion: number;
}

/** Sesiones por canal en orden fijo; lo que no está en CANALES (sin asignar, multired, otros pagos) va a «Otros». */
export function tramosCanal(d: Ga4Datos): Tramo[] {
  const conocidos = new Set(CANALES.map((c) => c.id));
  const tramos: Tramo[] = CANALES.map((c) => ({ ...c, sesiones: d.canales[c.id]?.sesiones ?? 0, interaccion: d.canales[c.id]?.interaccion ?? 0 }));
  const otros = Object.entries(d.canales)
    .filter(([k]) => !conocidos.has(k))
    .reduce((a, [, v]) => ({ sesiones: a.sesiones + v.sesiones, interaccion: a.interaccion + v.interaccion }), { sesiones: 0, interaccion: 0 });
  return [...tramos, { ...OTROS, ...otros }].filter((t) => t.sesiones > 0);
}

export const canal = (d: Ga4Datos, id: string) => d.canales[id] ?? { sesiones: 0, interaccion: 0 };

/**
 * Qué campañas de Google Ads llevan a cada sitio (marca + unidad de la campaña). Las de ISO de Peterson Control Union
 * apuntan a las páginas ISO de los sitios de Control Union de su país.
 */
export const SITIO_ADS: Record<string, { marcas: Marca[]; unidades: string[] }> = {
  'argentina.controlunion.com': { marcas: ['CU', 'PCU'], unidades: ['Argentina'] },
  'espana.controlunion.com': { marcas: ['CU', 'PCU'], unidades: ['España'] },
  'portugal.controlunion.com': { marcas: ['CU'], unidades: ['Portugal'] },
  'northamerica.controlunion.com': { marcas: ['CU'], unidades: ['Canadá', 'Estados Unidos'] },
  'americas.peterson-solutions.com': { marcas: ['PS'], unidades: ['Argentina'] },
};

/** Clics de Ads del mes hacia un sitio. null si el sitio no tiene campañas o si ese mes todavía no tiene gasto cargado. */
export function clicsAds(
  sitio: string,
  mes: string,
  campanas: { id: string; marca: Marca; unidad: string }[],
  metricas: { campanaId: string; mes: string; clics: number }[],
): number | null {
  const destino = SITIO_ADS[sitio];
  const delMes = metricas.filter((m) => m.mes === mes);
  if (!destino || !delMes.length) return null;
  const ids = new Set(campanas.filter((c) => destino.marcas.includes(c.marca) && destino.unidades.includes(c.unidad)).map((c) => c.id));
  return delMes.filter((m) => ids.has(m.campanaId)).reduce((a, m) => a + m.clics, 0);
}

export const tasa = (parte: number, total: number) => (total > 0 ? parte / total : 0);

export const esPaginaReal = (l: Ga4Landing) => l.pagina !== '(not set)' && l.pagina !== '';

export type Gravedad = 'alta' | 'media';
export interface Alerta {
  clave: string;
  gravedad: Gravedad;
  titulo: string;
  detalle: string;
}

// Umbrales: GA4 tiene que ver al menos 3 de cada 4 clics; bots cuando la mitad de las visitas son directas sin
// interacción; una página paga con menos de la mitad de visitas con interacción, sobre 20 visitas o más, pierde la
// mitad de lo que se paga.
export const UMBRAL_MEDICION = 0.75;
export const UMBRAL_BOTS = 0.5;
export const UMBRAL_LANDING = 0.5;
export const MIN_LANDING = 20;

/** Alertas de un sitio en un mes, de la más grave a la menos. */
export function alertas(d: Ga4Datos, clics: number | null): Alerta[] {
  const out: Alerta[] = [];
  const pago = canal(d, 'Paid Search');

  if (clics !== null && clics >= 30 && tasa(pago.sesiones, clics) < UMBRAL_MEDICION) {
    out.push({
      clave: 'medicion',
      gravedad: 'alta',
      titulo: `GA4 ve ${Math.round(tasa(pago.sesiones, clics) * 100)}% de los clics de Ads`,
      detalle: `${clics.toLocaleString('es-AR')} clics en Google Ads y ${pago.sesiones.toLocaleString('es-AR')} visitas pagas en GA4. Lo habitual es que se pierda el consentimiento de cookies (banner de la UE) o que la etiqueta no dispare en alguna landing: las conversiones de Ads se subestiman en la misma proporción.`,
    });
  }

  const bots = tasa(d.directo_sin_interaccion, d.sesiones);
  if (d.sesiones >= 200 && bots >= UMBRAL_BOTS) {
    out.push({
      clave: 'bots',
      gravedad: 'media',
      titulo: `${Math.round(bots * 100)}% de las visitas son directas sin interacción`,
      detalle: `${d.directo_sin_interaccion.toLocaleString('es-AR')} visitas directas que se van en segundos: son en su mayoría bots (Singapur, China, centros de datos de EE. UU.). Inflan las sesiones; para comparar sitios mirá las visitas con interacción.`,
    });
  }

  for (const l of d.landings_pagas.filter(esPaginaReal)) {
    if (l.sesiones >= MIN_LANDING && tasa(l.interaccion, l.sesiones) < UMBRAL_LANDING) {
      out.push({
        clave: `landing:${l.pagina}`,
        gravedad: 'media',
        titulo: `Landing paga con poca interacción: ${l.pagina}`,
        detalle: `${l.sesiones} visitas pagas y solo ${Math.round(tasa(l.interaccion, l.sesiones) * 100)}% con interacción. Revisar que el anuncio prometa lo que muestra la página, la velocidad en el celular y que el contacto esté arriba.`,
      });
    }
  }

  if (pago.sesiones >= 50 && !(d.contactos['Paid Search']?.formularios || d.contactos['Paid Search']?.emails)) {
    out.push({
      clave: 'pago-sin-contactos',
      gravedad: 'media',
      titulo: `${pago.sesiones.toLocaleString('es-AR')} visitas pagas y ningún contacto medido`,
      detalle: 'Ads trae tráfico pero GA4 no registra formularios ni emails desde esas visitas. Si el formulario es de HubSpot (iframe) no llega a GA4: hay que medirlo con el evento de envío de HubSpot o con las conversiones de HubSpot importadas a Ads.',
    });
  } else if (d.sesiones >= 300 && d.contactos_total === 0) {
    out.push({
      clave: 'sin-contactos',
      gravedad: 'media',
      titulo: 'Ningún contacto medido en el mes',
      detalle: 'GA4 no registra formularios ni emails en todo el sitio. Probablemente el formulario es de HubSpot (iframe) y no envía eventos a GA4.',
    });
  }

  return out.sort((a, b) => (a.gravedad === b.gravedad ? 0 : a.gravedad === 'alta' ? -1 : 1));
}

/** Suma de varios sitio-mes, para las cifras de arriba. */
export function totales(lista: Ga4Datos[]) {
  return lista.reduce(
    (a, d) => ({
      sesiones: a.sesiones + d.sesiones,
      interaccion: a.interaccion + d.interaccion,
      contactos: a.contactos + d.contactos_total,
      organico: a.organico + canal(d, 'Organic Search').sesiones,
    }),
    { sesiones: 0, interaccion: 0, contactos: 0, organico: 0 },
  );
}

export interface MesGa4 {
  mes: string;
  dias: number;
  diasMes: number;
  sesiones: number;
  interaccion: number;
  contactos: number;
  /** Visitas con interacción por canal (los mismos tramos que la barra de canales). */
  canales: Record<string, number>;
}

/** Totales por mes de los sitios elegidos, del más viejo al más nuevo. */
export function serieSitios(lista: { mes: string; dias: number; datos: Ga4Datos }[]): MesGa4[] {
  const porMes = new Map<string, MesGa4>();
  for (const s of lista) {
    const [a, m] = s.mes.split('-').map(Number);
    let t = porMes.get(s.mes);
    if (!t) porMes.set(s.mes, (t = { mes: s.mes, dias: s.dias, diasMes: new Date(a, m, 0).getDate(), sesiones: 0, interaccion: 0, contactos: 0, canales: {} }));
    t.dias = Math.max(t.dias, s.dias);
    t.sesiones += s.datos.sesiones;
    t.interaccion += s.datos.interaccion;
    t.contactos += s.datos.contactos_total;
    for (const tr of tramosCanal(s.datos)) t.canales[tr.id] = (t.canales[tr.id] ?? 0) + tr.interaccion;
  }
  return [...porMes.values()].sort((x, y) => x.mes.localeCompare(y.mes));
}
