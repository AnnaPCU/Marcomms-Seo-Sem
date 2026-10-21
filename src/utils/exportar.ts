/**
 * Arma el contenido del Excel que exporta el tablero: todas las tarjetas visibles con todo su contenido, el historial
 * de cada una y una hoja «Léeme» con el contexto (pensado para pasárselo a Claude en otra conversación).
 * Sin dependencias de React ni de la librería de Excel; se testea en exportar.test.ts. El archivo lo escribe
 * components/tablero/BotonExportar.tsx.
 */
import { ACCIONES, ESTADO_BY_ID, ESTADOS, MARCA_BY_ID, PRIORIDAD_BY_ID, accionesDe } from '@/constants/estados';
import type { Evento, Recomendacion } from '@/services/recomendaciones';
import { fechaHora, mesCorto } from '@/utils/formato';

export type Celda = string | number | null;

export interface Hoja {
  nombre: string;
  encabezado: string[];
  filas: Celda[][];
  /** Ancho de cada columna en caracteres. */
  anchos: number[];
}

export interface ContextoExport {
  vista: string; // 'SEM · campañas'
  filtros: { etiqueta: string; valor: string }[];
  campana: (r: Recomendacion) => string | null;
  grupo: (r: Recomendacion) => string | null;
  pais: (r: Recomendacion) => string | null;
  ahora?: Date;
}

// Excel no acepta más de 32.767 caracteres por celda.
const MAX_CELDA = 32_000;

/** Nombre legible de cada dato de la evidencia, en el orden en que se muestran. Lo que no está acá va al final con su clave. */
export const CAMPOS_EVIDENCIA: [string, string][] = [
  ['ficha', 'Tipo de ficha'],
  ['unidad', 'Unidad (país)'],
  ['estado_en_plan', 'Estado en el plan'],
  ['pain', 'Problema'],
  ['pain_txt', 'Problema · detalle'],
  ['mejora', 'Mejora'],
  ['mejora_txt', 'Mejora · detalle'],
  ['cambio', 'Cambio propuesto'],
  ['gasto_ars', 'Gasto analizado (ARS)'],
  ['ventanas', 'Período analizado'],
  ['url', 'URL final'],
  ['fuerza', 'Fuerza del anuncio'],
  ['titulos_hoy', 'Títulos actuales'],
  ['terminos', 'Términos de búsqueda que lo activaron'],
  ['diagnostico', 'Diagnóstico'],
  ['quitar', 'Qué quitar'],
  ['titulos_propuestos', 'Títulos propuestos'],
  ['descripciones_propuestas', 'Descripciones propuestas'],
  ['organico', 'Cómo lo buscan en orgánico'],
  ['organico_desde', 'Orgánico medido desde'],
  ['organico_hasta', 'Orgánico hasta'],
  ['nota', 'Nota'],
];
// ya van en sus propias columnas
const OMITIR = new Set(['acciones']);

const recortar = (s: string) => (s.length > MAX_CELDA ? s.slice(0, MAX_CELDA) + ' […recortado: el texto completo está en «Evidencia completa (JSON)»]' : s);

/** Un valor de la evidencia como texto de celda, sin perder nada: listas una por línea, objetos como «clave: valor». */
export function aCelda(v: unknown): Celda {
  if (v === null || v === undefined) return null;
  if (typeof v === 'number') return v;
  if (typeof v === 'boolean') return v ? 'sí' : 'no';
  if (typeof v === 'string') return recortar(v);
  if (Array.isArray(v)) {
    if (!v.length) return null;
    return recortar(
      v
        .map((x) =>
          x && typeof x === 'object' && !Array.isArray(x)
            ? Object.entries(x as Record<string, unknown>)
                .map(([k, y]) => `${k}: ${typeof y === 'object' ? JSON.stringify(y) : String(y)}`)
                .join(' · ')
            : typeof x === 'object'
              ? JSON.stringify(x)
              : String(x),
        )
        .join('\n'),
    );
  }
  return recortar(JSON.stringify(v));
}

/** Claves de evidencia presentes en la lista, en el orden de CAMPOS_EVIDENCIA y las desconocidas al final. */
export function clavesEvidencia(recs: Recomendacion[]): [string, string][] {
  const presentes = new Set(recs.flatMap((r) => Object.keys(r.evidencia)).filter((k) => !OMITIR.has(k)));
  const conocidas = CAMPOS_EVIDENCIA.filter(([k]) => presentes.has(k));
  const otras = [...presentes].filter((k) => !CAMPOS_EVIDENCIA.some(([c]) => c === k)).sort();
  return [...conocidas, ...otras.map((k): [string, string] => [k, k])];
}

const etiquetaAcciones = (r: Recomendacion) =>
  accionesDe(r.evidencia)
    .map((id) => ACCIONES.find((a) => a.id === id)?.label ?? id)
    .join(', ') || null;

export function hojaTareas(recs: Recomendacion[], ctx: ContextoExport): Hoja {
  const ev = clavesEvidencia(recs);
  const base: [string, number, (r: Recomendacion) => Celda][] = [
    ['Clave', 26, (r) => r.clave],
    ['Tipo', 6, (r) => r.tipo],
    ['Cliente', 22, (r) => MARCA_BY_ID[r.marca]?.label ?? r.marca],
    ['País', 14, (r) => ctx.pais(r)],
    ['Campaña', 34, (r) => ctx.campana(r)],
    ['Grupo de anuncios', 22, (r) => ctx.grupo(r)],
    ['Sitio', 24, (r) => r.sitio],
    ['Página', 30, (r) => r.pagina],
    ['Título', 40, (r) => r.titulo],
    ['Detalle', 70, (r) => recortar(r.detalle)],
    ['Estado', 12, (r) => ESTADO_BY_ID[r.estado]?.label ?? r.estado],
    ['Prioridad', 10, (r) => PRIORIDAD_BY_ID[r.prioridad]?.label ?? r.prioridad],
    ['Tipo de mejora', 24, etiquetaAcciones],
    ['Mes de alta', 11, (r) => mesCorto(r.mesAlta)],
    ['Mes de cierre', 11, (r) => (r.mesCierre ? mesCorto(r.mesCierre) : null)],
    ['Motivo de descarte', 30, (r) => r.motivoDescarte],
    ['Verificada por la API', 10, (r) => (r.verificadaApi ? 'sí' : 'no')],
    ['Verificada el', 18, (r) => (r.verificadaEn ? fechaHora(r.verificadaEn) : null)],
    ['Origen', 22, (r) => r.origen],
    ['Orden en la columna', 8, (r) => r.orden],
    ['Último cambio por', 18, (r) => r.actualizadaPor],
    ['Último cambio', 18, (r) => fechaHora(r.updatedAt)],
  ];
  const ordenEstado = (r: Recomendacion) => ESTADOS.findIndex((e) => e.id === r.estado);
  const lista = [...recs].sort((a, b) => ordenEstado(a) - ordenEstado(b) || a.orden - b.orden);
  return {
    nombre: 'Tareas',
    encabezado: [...base.map((c) => c[0]), ...ev.map(([, l]) => l), 'Evidencia completa (JSON)'],
    anchos: [...base.map((c) => c[1]), ...ev.map(([k]) => (['terminos', 'organico', 'titulos_propuestos', 'descripciones_propuestas', 'diagnostico', 'pain_txt', 'mejora_txt'].includes(k) ? 50 : 22)), 60],
    filas: lista.map((r) => [...base.map((c) => c[2](r)), ...ev.map(([k]) => aCelda(r.evidencia[k])), recortar(JSON.stringify(r.evidencia))]),
  };
}

export function hojaHistorial(recs: Recomendacion[], eventos: Evento[]): Hoja {
  const porId = new Map(recs.map((r) => [r.id, r]));
  const est = (e: string | null) => (e ? (ESTADO_BY_ID[e as keyof typeof ESTADO_BY_ID]?.label ?? e) : '—');
  return {
    nombre: 'Historial',
    encabezado: ['Clave', 'Título', 'Fecha', 'De', 'A', 'Motivo', 'Quién'],
    anchos: [26, 40, 18, 12, 12, 40, 20],
    filas: [...eventos]
      .filter((e) => porId.has(e.recomendacionId))
      .sort((a, b) => a.creadoEn.localeCompare(b.creadoEn))
      .map((e) => {
        const r = porId.get(e.recomendacionId)!;
        return [r.clave, r.titulo, fechaHora(e.creadoEn), est(e.deEstado), est(e.aEstado), e.motivo, e.usuario];
      }),
  };
}

export function hojaLeeme(recs: Recomendacion[], eventos: number, ctx: ContextoExport): Hoja {
  const ahora = ctx.ahora ?? new Date();
  const filas: Celda[][] = [
    ['Qué es', 'Exportación del tablero Marcomms SEO-SEM (MarComms): mejoras de Google Ads y SEO para Control Union, Peterson Control Union (ISO) y Peterson Solutions.'],
    ['Vista', ctx.vista],
    ['Exportado el', fechaHora(ahora.toISOString())],
    ['Filtros aplicados', ctx.filtros.length ? ctx.filtros.map((f) => `${f.etiqueta}: ${f.valor}`).join(' · ') : 'ninguno (todas las tarjetas)'],
    ['Tarjetas', recs.length],
    ...ESTADOS.map((e): Celda[] => [`· ${e.label}`, `${recs.filter((r) => r.estado === e.id).length} — ${e.hint}`]),
    ['Movimientos en el historial', eventos],
    [null, null],
    ['Hoja «Tareas»', 'Una fila por tarjeta, con todo su contenido. Las columnas de la derecha son la evidencia del análisis (términos de búsqueda, títulos actuales y propuestos, diagnóstico, búsquedas orgánicas…); la última, «Evidencia completa (JSON)», la tiene entera sin formato.'],
    ['Hoja «Historial»', 'Cada cambio de estado de esas tarjetas: cuándo, de qué estado a cuál, quién y por qué.'],
    ['Marcas', 'Control Union certifica, audita, inspecciona y verifica (nunca «asesora»). Peterson Solutions es consultora: acompaña y prepara para certificar (nunca «certifica»). No se mezclan.'],
    ['Montos', 'En pesos argentinos (ARS). Lo que vino de la cuenta anterior de Google Ads, en euros, está convertido con el tipo de cambio oficial del BCRA, promedio del mes.'],
  ];
  return { nombre: 'Léeme', encabezado: ['Campo', 'Valor'], anchos: [28, 110], filas };
}

/** Nombre del archivo: SEM_CU_España_2026-10-21.xlsx */
export function nombreArchivo(tipo: string, partes: string[], ahora = new Date()): string {
  const limpio = (s: string) => s.replace(/[\\/:*?"<>|]+/g, '').replace(/\s+/g, '-');
  const fecha = `${ahora.getFullYear()}-${String(ahora.getMonth() + 1).padStart(2, '0')}-${String(ahora.getDate()).padStart(2, '0')}`;
  return [tipo, ...partes.filter(Boolean).map(limpio), fecha].join('_') + '.xlsx';
}
