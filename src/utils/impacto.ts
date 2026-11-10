/**
 * Impacto de las optimizaciones SEM marcadas como «hecha».
 *
 * «Hecha» no quiere decir que se cargó todo: el equipo la marca así cuando aplicó la mayor parte. Por eso cada ítem de la
 * tarjeta se cruza con el historial de cambios de Google Ads (change_event) para saber qué se implementó de verdad, y
 * el antes / después se mide desde la fecha real de esos cambios, no desde el día en que se movió la tarjeta.
 *
 * Ventanas: «antes» = los 28 días previos al primer cambio aplicado; «después» = desde el día siguiente al último cambio
 * hasta 28 días o hasta el último día con datos (mínimo 14 para dar un resultado). Los días entre el primer y el último cambio son transición y no cuentan.
 * Se compara por día (promedios), porque las ventanas pueden tener largos distintos. En metricas_dia un día sin fila es
 * un día sin impresiones (Google lo omite): cuenta como cero.
 *
 * Todo es puro y se testea en impacto.test.ts.
 */
import type { CambioAds } from '@/services/cambios';
import type { Evento, Recomendacion } from '@/services/recomendaciones';
import type { MetricaDia } from '@/services/metricas';

export const DIAS_VENTANA = 28;
/** Dos semanas completas: con menos, un fin de semana o un día raro mueven todo. */
export const MIN_DIAS_DESPUES = 14;
/** Variación a partir de la cual un CTR o un CPC se considera un cambio y no ruido. */
export const UMBRAL = 0.1;

// ───────────────────────────────────────────────────────────── fechas (AAAA-MM-DD, sin husos)
export function sumarDias(f: string, n: number): string {
  const d = new Date(f + 'T12:00:00Z');
  d.setUTCDate(d.getUTCDate() + n);
  return d.toISOString().slice(0, 10);
}

export function diasEntre(desde: string, hasta: string): number {
  return Math.round((Date.parse(hasta + 'T12:00:00Z') - Date.parse(desde + 'T12:00:00Z')) / 86_400_000) + 1;
}

/** Fecha en hora de Argentina (UTC−3, sin horario de verano) de un instante ISO. */
export function fechaArgentina(iso: string): string {
  return new Date(Date.parse(iso) - 3 * 3_600_000).toISOString().slice(0, 10);
}

// ───────────────────────────────────────────────────────────── ítems de la tarjeta
export interface ItemTarjeta {
  paso: number;
  tituloPaso: string;
  accion: string;
  tipo: string;
  texto: string;
  concordancia?: string;
  destino?: string;
  reemplaza?: string;
  opcional?: boolean;
  prioritario?: boolean;
}

/** aplicado = se ve en el historial de Ads · no_visto = no aparece · a_criterio = decisión o ajuste que no se puede verificar solo. */
export type EstadoItem = 'aplicado' | 'no_visto' | 'a_criterio';

export interface ItemCruzado extends ItemTarjeta {
  estado: EstadoItem;
  cambio?: CambioAds;
  nota?: string;
}

export function itemsDeTarjeta(rec: Pick<Recomendacion, 'evidencia'>): ItemTarjeta[] {
  const pasos = Array.isArray(rec.evidencia?.pasos) ? (rec.evidencia.pasos as Record<string, unknown>[]) : [];
  const out: ItemTarjeta[] = [];
  pasos.forEach((p, i) => {
    const items = Array.isArray(p.items) ? (p.items as Record<string, unknown>[]) : [];
    for (const it of items) {
      if (typeof it.texto !== 'string' || !it.texto) continue;
      out.push({
        paso: i + 1,
        tituloPaso: typeof p.titulo === 'string' ? p.titulo : `Paso ${i + 1}`,
        accion: String(it.accion ?? ''),
        tipo: String(it.tipo ?? ''),
        texto: it.texto,
        concordancia: typeof it.concordancia === 'string' ? it.concordancia : undefined,
        destino: typeof it.destino === 'string' ? it.destino : undefined,
        reemplaza: typeof it.reemplaza === 'string' ? it.reemplaza : undefined,
        opcional: it.opcional === true,
        prioritario: it.prioritario === true,
      });
    }
  });
  return out;
}

// ───────────────────────────────────────────────────────────── cruce con el historial de Ads
const sinTildes = (t: string) => t.normalize('NFD').replace(/[̀-ͯ]/g, '');

/** Keyword o negativa comparable: sin tildes, minúsculas, sin [ ] « » ni comillas, espacios simples. Conserva el «+» de «gmp+». */
export function normalizarKeyword(t: string): string {
  return sinTildes(t).toLowerCase().replace(/[[\]«»"“”]/g, ' ').replace(/\s+/g, ' ').trim();
}

/** Texto de anuncio comparable: además quita la puntuación («EE. UU.» = «EE.UU»). */
export function normalizarTexto(t: string): string {
  return sinTildes(t).toLowerCase().replace(/[^a-z0-9+]+/g, '');
}

function mismoTextoAnuncio(a: string, b: string): boolean {
  const x = normalizarTexto(a);
  const y = normalizarTexto(b);
  if (!x || !y) return false;
  if (x === y) return true;
  // Google o quien carga a veces recorta una palabra: se acepta si uno contiene al otro y difieren poco.
  const [corto, largo] = x.length <= y.length ? [x, y] : [y, x];
  return corto.length >= 12 && largo.includes(corto) && corto.length / largo.length >= 0.85;
}

function mismaUrl(a: string, b: string): boolean {
  const n = (u: string) => u.trim().toLowerCase().replace(/^https?:\/\//, '').replace(/\/+$/, '');
  return n(a) === n(b);
}

const esCriterio = (c: CambioAds) => c.recurso === 'AD_GROUP_CRITERION' || c.recurso === 'CAMPAIGN_CRITERION';
const esAnuncio = (c: CambioAds) => c.recurso === 'AD' || c.recurso === 'AD_GROUP_AD';

function buscarKeyword(item: ItemTarjeta, cambios: CambioAds[], negativa: boolean, pausa: boolean): CambioAds | undefined {
  const t = normalizarKeyword(item.texto);
  const candidatos = cambios.filter((c) => {
    if (!esCriterio(c) || !c.detalle.texto || normalizarKeyword(c.detalle.texto) !== t) return false;
    if (Boolean(c.detalle.negativa) !== negativa) return false;
    if (pausa) return c.operacion === 'REMOVE' || c.detalle.estado_despues === 'PAUSED' || c.detalle.estado_despues === 'REMOVED';
    return (c.operacion === 'CREATE' && c.detalle.estado_despues !== 'PAUSED') ||
      (c.operacion === 'UPDATE' && c.detalle.estado_antes === 'PAUSED' && c.detalle.estado_despues === 'ENABLED');
  });
  // Si se cargó la misma keyword en dos concordancias, cada ítem toma la suya.
  return candidatos.find((c) => item.concordancia && c.detalle.concordancia === item.concordancia) ?? candidatos[0];
}

/** Busca en los cambios de la campaña el que corresponde al ítem. */
export function cruzarItem(item: ItemTarjeta, cambios: CambioAds[]): ItemCruzado {
  const decision = item.accion === 'decidir';
  let cambio: CambioAds | undefined;
  let nota: string | undefined;

  if (item.tipo === 'negativa' && (item.accion === 'agregar' || decision)) {
    cambio = buscarKeyword(item, cambios, true, false);
  } else if (item.tipo === 'keyword' && item.accion === 'pausar') {
    cambio = buscarKeyword(item, cambios, false, true);
  } else if (item.tipo === 'keyword' && (item.accion === 'agregar' || decision)) {
    cambio = buscarKeyword(item, cambios, false, false);
  } else if (item.tipo === 'titulo' || item.tipo === 'descripcion') {
    const campo = item.tipo === 'titulo' ? 'titulos_agregados' : 'descripciones_agregadas';
    cambio = cambios.find((c) => esAnuncio(c) && (c.detalle[campo] ?? []).some((x) => mismoTextoAnuncio(x, item.texto)));
  } else if (item.tipo === 'grupo' && item.accion === 'crear') {
    const n = normalizarKeyword(item.texto);
    cambio = cambios.find((c) => c.recurso === 'AD_GROUP' && c.operacion === 'CREATE' &&
      [c.detalle.nombre, c.grupo].some((x) => x && normalizarKeyword(x) === n));
  } else if (/^https?:\/\//i.test(item.texto.trim())) {
    cambio = cambios.find((c) => esAnuncio(c) && (c.detalle.urls_despues ?? []).some((u) => mismaUrl(u, item.texto)));
  } else {
    return { ...item, estado: 'a_criterio', nota: decision ? 'Decisión del equipo: no se verifica sola' : 'Ajuste de configuración: no se verifica solo' };
  }

  if (cambio && item.concordancia && cambio.detalle.concordancia && cambio.detalle.concordancia !== item.concordancia &&
    (item.tipo === 'keyword' || item.tipo === 'negativa')) {
    nota = `Cargada como ${cambio.detalle.concordancia} (se proponía ${item.concordancia})`;
  }
  if (cambio) return { ...item, estado: 'aplicado', cambio, nota };
  if (decision) return { ...item, estado: 'a_criterio', nota: 'Se decidió no cargarla (o no se ve en Ads)' };
  return { ...item, estado: 'no_visto' };
}

// ───────────────────────────────────────────────────────────── antes / después
export interface Ventana {
  desde: string;
  hasta: string;
  dias: number;
  coste: number;
  clics: number;
  impresiones: number;
  conversiones: number;
}

export interface Indicadores {
  costeDia: number;
  clicsDia: number;
  imprDia: number;
  convDia: number;
  ctr: number | null;
  cpc: number | null;
}

export function indicadores(v: Ventana): Indicadores {
  const d = v.dias || 1;
  return {
    costeDia: v.coste / d,
    clicsDia: v.clics / d,
    imprDia: v.impresiones / d,
    convDia: v.conversiones / d,
    ctr: v.impresiones ? v.clics / v.impresiones : null,
    cpc: v.clics ? v.coste / v.clics : null,
  };
}

export function sumarVentana(metricas: MetricaDia[], campanaId: string, desde: string, hasta: string): Ventana {
  const v: Ventana = { desde, hasta, dias: Math.max(0, diasEntre(desde, hasta)), coste: 0, clics: 0, impresiones: 0, conversiones: 0 };
  if (v.dias === 0) return v;
  for (const m of metricas) {
    if (m.campanaId !== campanaId || m.fecha < desde || m.fecha > hasta) continue;
    v.coste += m.coste;
    v.clics += m.clics;
    v.impresiones += m.impresiones;
    v.conversiones += m.conversiones;
  }
  return v;
}

/** Variación relativa; null si no hay base. */
export function variacion(antes: number | null, despues: number | null): number | null {
  if (antes === null || despues === null || antes === 0) return null;
  return despues / antes - 1;
}

export type Veredicto = 'positivo' | 'negativo' | 'neutro' | 'midiendo' | 'sin_datos';

export interface Juicio {
  veredicto: Veredicto;
  razones: string[];
  /** Menos de 10 clics en alguna de las dos ventanas: la dirección vale, el número no. */
  senalDebil: boolean;
}

const pctTxt = (v: number) => (v > 0 ? '+' : '−') + Math.abs(Math.round(v * 100)) + '%';

/**
 * Puntaje simple y explicable: conversiones por día (pesan doble), CTR y CPC. Gana el signo del total.
 * Bajar el gasto no cuenta como bueno ni malo por sí solo: muchas optimizaciones lo bajan a propósito (negativas, pausas).
 */
export function juzgar(antes: Ventana, despues: Ventana): Juicio {
  if (despues.dias < MIN_DIAS_DESPUES) return { veredicto: 'midiendo', razones: [`${Math.max(0, despues.dias)} de ${MIN_DIAS_DESPUES} días mínimos de datos después del cambio`], senalDebil: true };
  if (antes.impresiones === 0 && despues.impresiones === 0) return { veredicto: 'sin_datos', razones: ['Sin impresiones antes ni después'], senalDebil: true };
  const a = indicadores(antes);
  const d = indicadores(despues);
  let puntos = 0;
  const razones: string[] = [];

  if (antes.conversiones + despues.conversiones > 0) {
    if (d.convDia > a.convDia && despues.conversiones >= 1) {
      puntos += 2;
      razones.push(`Conversiones: ${antes.conversiones} en ${antes.dias} días → ${despues.conversiones} en ${despues.dias} días`);
    } else if (d.convDia < a.convDia && antes.conversiones >= 2) {
      puntos -= 2;
      razones.push(`Conversiones: ${antes.conversiones} en ${antes.dias} días → ${despues.conversiones} en ${despues.dias} días`);
    }
  }
  const vCtr = variacion(a.ctr, d.ctr);
  if (vCtr !== null && Math.abs(vCtr) >= UMBRAL) {
    puntos += vCtr > 0 ? 1 : -1;
    razones.push(`CTR ${pctTxt(vCtr)} (${((a.ctr ?? 0) * 100).toFixed(1)}% → ${((d.ctr ?? 0) * 100).toFixed(1)}%)`);
  }
  const vCpc = variacion(a.cpc, d.cpc);
  if (vCpc !== null && Math.abs(vCpc) >= UMBRAL) {
    puntos += vCpc < 0 ? 1 : -1;
    razones.push(`CPC ${pctTxt(vCpc)}`);
  }
  if (a.clicsDia > 0 && d.clicsDia === 0) {
    puntos -= 1;
    razones.push('Sin clics después del cambio');
  }
  if (!razones.length) razones.push('CTR, CPC y conversiones se movieron menos de 10%');
  return {
    veredicto: puntos > 0 ? 'positivo' : puntos < 0 ? 'negativo' : 'neutro',
    razones,
    senalDebil: antes.clics < 10 || despues.clics < 10,
  };
}

// ───────────────────────────────────────────────────────────── por tarjeta
export interface ImpactoTarjeta {
  rec: Recomendacion;
  campanaId: string;
  /** Día (hora Argentina) en que la tarjeta pasó a «hecha». */
  fechaHecha: string;
  items: ItemCruzado[];
  aplicados: number;
  /** Ítems que se pueden verificar contra Ads (los «a criterio» no cuentan). */
  verificables: number;
  primerCambio: string | null;
  ultimoCambio: string | null;
  antes: Ventana | null;
  despues: Ventana | null;
  juicio: Juicio;
  /** Otros cambios en la campaña durante la implementación que no corresponden a un ítem (el equipo pudo sumar cosas). */
  otrosCambios: CambioAds[];
  avisos: string[];
}

export interface EntradaImpacto {
  recs: Recomendacion[];
  eventos: Evento[];
  cambios: CambioAds[];
  metricas: MetricaDia[];
}

/** Primer y último día con datos diarios cargados (para no medir días que todavía no se extrajeron). */
export function rangoDatos(metricas: MetricaDia[]): { desde: string; hasta: string } | null {
  if (!metricas.length) return null;
  let desde = metricas[0].fecha;
  let hasta = metricas[0].fecha;
  for (const m of metricas) {
    if (m.fecha < desde) desde = m.fecha;
    if (m.fecha > hasta) hasta = m.fecha;
  }
  return { desde, hasta };
}

export function impactoDeTarjeta(rec: Recomendacion, eventos: Evento[], cambios: CambioAds[], metricas: MetricaDia[], rango: { desde: string; hasta: string } | null): ImpactoTarjeta | null {
  if (!rec.campanaId) return null;
  const propios = eventos.filter((e) => e.recomendacionId === rec.id);
  const hechas = propios.filter((e) => e.aEstado === 'hecha').map((e) => e.creadoEn).sort();
  const fechaHecha = fechaArgentina(hechas.length ? hechas[hechas.length - 1] : rec.updatedAt);
  const enProceso = propios.filter((e) => e.aEstado === 'en_proceso').map((e) => fechaArgentina(e.creadoEn)).sort();
  // Los cambios cuentan desde unos días antes de empezar (a veces se carga y después se mueve la tarjeta) hasta dos semanas después.
  const inicio = sumarDias(enProceso[0] && enProceso[0] < fechaHecha ? enProceso[0] : fechaHecha, -3);
  const fin = sumarDias(fechaHecha, 14);
  const enVentana = cambios
    .filter((c) => c.campanaId === rec.campanaId && c.fecha.slice(0, 10) >= inicio && c.fecha.slice(0, 10) <= fin)
    .sort((a, b) => a.fecha.localeCompare(b.fecha));

  const items = itemsDeTarjeta(rec).map((it) => cruzarItem(it, enVentana));
  const usados = new Set(items.map((i) => i.cambio?.id).filter(Boolean));
  const aplicadosC = items.filter((i) => i.cambio).map((i) => i.cambio!.fecha.slice(0, 10)).sort();
  const verificables = items.filter((i) => i.estado !== 'a_criterio').length;
  const avisos: string[] = [];

  const primerCambio = aplicadosC[0] ?? null;
  const ultimoCambio = aplicadosC[aplicadosC.length - 1] ?? null;
  const corteA = primerCambio ?? fechaHecha;
  const corteD = ultimoCambio ?? fechaHecha;
  if (!primerCambio) avisos.push('No se ve ningún ítem en el historial de Ads: se mide desde el día en que se marcó como hecha.');

  let antes: Ventana | null = null;
  let despues: Ventana | null = null;
  let juicio: Juicio = { veredicto: 'sin_datos', razones: ['Sin datos diarios cargados'], senalDebil: true };
  if (rango) {
    const aDesde = [sumarDias(corteA, -DIAS_VENTANA), rango.desde].sort()[1];
    antes = sumarVentana(metricas, rec.campanaId, aDesde, sumarDias(corteA, -1));
    const dDesde = sumarDias(corteD, 1);
    const dHasta = [sumarDias(corteD, DIAS_VENTANA), rango.hasta].sort()[0];
    despues = dHasta >= dDesde ? sumarVentana(metricas, rec.campanaId, dDesde, dHasta) : { ...sumarVentana(metricas, rec.campanaId, dDesde, dDesde), dias: 0 };
    juicio = juzgar(antes, despues);
    const presup = cambios.filter((c) => c.campanaId === rec.campanaId && c.recurso === 'CAMPAIGN_BUDGET' &&
      c.fecha.slice(0, 10) >= antes!.desde && c.fecha.slice(0, 10) <= (despues!.dias ? despues!.hasta : corteD));
    for (const c of presup) avisos.push(`El presupuesto diario cambió el ${c.fecha.slice(8, 10)}/${c.fecha.slice(5, 7)} (${c.resumen.replace(/^Presupuesto diario: /, '')}): parte de la diferencia es por eso.`);
  }
  return {
    rec,
    campanaId: rec.campanaId,
    fechaHecha,
    items,
    aplicados: items.filter((i) => i.estado === 'aplicado').length,
    verificables,
    primerCambio,
    ultimoCambio,
    antes,
    despues,
    juicio,
    otrosCambios: enVentana.filter((c) => !usados.has(c.id)),
    avisos,
  };
}

/** Día en que la tarjeta junta los días mínimos después del último cambio (para «Próximamente»). */
export function fechaResultado(x: ImpactoTarjeta): string {
  return sumarDias(x.ultimoCambio ?? x.fechaHecha, MIN_DIAS_DESPUES);
}

/** Todas las tarjetas SEM «hechas» con campaña, de la más reciente a la más vieja. */
export function calcularImpacto({ recs, eventos, cambios, metricas }: EntradaImpacto): ImpactoTarjeta[] {
  const rango = rangoDatos(metricas);
  return recs
    .filter((r) => r.tipo === 'SEM' && r.estado === 'hecha' && r.campanaId)
    .map((r) => impactoDeTarjeta(r, eventos, cambios, metricas, rango))
    .filter((x): x is ImpactoTarjeta => x !== null)
    .sort((a, b) => b.fechaHecha.localeCompare(a.fechaHecha) || a.rec.titulo.localeCompare(b.rec.titulo));
}
