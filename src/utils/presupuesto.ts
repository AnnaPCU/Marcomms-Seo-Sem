/**
 * Cálculos del seguimiento de presupuesto. Funciones puras, sin React ni Supabase (se testean en presupuesto.test.ts).
 *
 * Definiciones:
 *  - presupuesto diario: el configurado en Google Ads. Solo cuenta si la campaña está activa (ENABLED).
 *  - ritmo: gasto por día (sobre los días con datos) ÷ presupuesto diario. 1 = gasta justo lo asignado.
 *  - consumo del mes: gasto acumulado ÷ presupuesto del mes completo (presupuesto diario × días del mes).
 *  - semáforo: rojo si el ritmo supera UMBRAL_SOBRE o si no gasta nada; verde en el medio; gris sin presupuesto.
 */

export const UMBRAL_SOBRE = 1.05;
export const UMBRAL_TOPE = 0.95; // a partir de acá la campaña está limitada por presupuesto
export const UMBRAL_OCIOSO = 0.5; // por debajo, sobra presupuesto que se puede rotar

export type Semaforo = 'rojo' | 'verde' | 'gris';

export interface CampanaGasto {
  id: string;
  nombre: string;
  marca: string;
  unidad: string;
  estado: string;
  presupuestoDia: number | null;
  coste: number;
  clics: number;
  conv: number;
  impresiones?: number;
}

export interface GrupoGasto {
  campanaId: string;
  nombre: string;
  coste: number;
  clics: number;
  conv: number;
}

export interface Nodo {
  clave: string;
  nombre: string;
  nivel: 1 | 2 | 3 | 4;
  coste: number;
  clics: number;
  conv: number;
  /** Suma del presupuesto diario de las campañas activas debajo de este nodo; null si no hay ninguna. */
  presDia: number | null;
  estado?: string;
  campanaId?: string;
  hijos: Nodo[];
}

/** Presupuesto diario que cuenta: solo campañas activas. */
export function presupuestoActivo(c: Pick<CampanaGasto, 'estado' | 'presupuestoDia'>): number | null {
  return c.estado === 'ENABLED' && c.presupuestoDia && c.presupuestoDia > 0 ? c.presupuestoDia : null;
}

export function ritmo(coste: number, presDia: number | null, dias: number): number | null {
  if (!presDia || dias <= 0) return null;
  return coste / dias / presDia;
}

export function consumoMes(coste: number, presDia: number | null, diasMes: number): number | null {
  if (!presDia || diasMes <= 0) return null;
  return coste / (presDia * diasMes);
}

export function semaforo(coste: number, presDia: number | null, dias: number): Semaforo {
  const r = ritmo(coste, presDia, dias);
  if (r === null) return 'gris';
  if (coste <= 0 || r > UMBRAL_SOBRE) return 'rojo';
  return 'verde';
}

/** Días del mes calendario de un 'AAAA-MM'. */
export function diasDelMes(mes: string): number {
  const [a, m] = mes.split('-').map(Number);
  return new Date(a, m, 0).getDate();
}

function nuevoNodo(clave: string, nombre: string, nivel: Nodo['nivel']): Nodo {
  return { clave, nombre, nivel, coste: 0, clics: 0, conv: 0, presDia: null, hijos: [] };
}

function sumar(n: Nodo, x: { coste: number; clics: number; conv: number }, presDia: number | null) {
  n.coste += x.coste;
  n.clics += x.clics;
  n.conv += x.conv;
  if (presDia !== null) n.presDia = (n.presDia ?? 0) + presDia;
}

/**
 * Árbol cliente → país → campaña → grupo. Las campañas salen del catálogo (así aparecen también las que no gastaron)
 * y los grupos cuelgan de su campaña. Cada nivel se ordena por gasto.
 */
export function armarArbol(campanas: CampanaGasto[], grupos: GrupoGasto[], ordenMarcas: string[] = []): Nodo[] {
  const clientes = new Map<string, Nodo>();
  const porCampana = new Map<string, Nodo>();
  for (const c of campanas) {
    const pres = presupuestoActivo(c);
    const cli = clientes.get(c.marca) ?? nuevoNodo(c.marca, c.marca, 1);
    clientes.set(c.marca, cli);
    let pais = cli.hijos.find((h) => h.nombre === c.unidad);
    if (!pais) {
      pais = nuevoNodo(`${c.marca}|${c.unidad}`, c.unidad, 2);
      cli.hijos.push(pais);
    }
    const camp: Nodo = { ...nuevoNodo(c.id, c.nombre, 3), estado: c.estado, campanaId: c.id };
    sumar(camp, c, pres);
    sumar(pais, c, pres);
    sumar(cli, c, pres);
    pais.hijos.push(camp);
    porCampana.set(c.id, camp);
  }
  for (const g of grupos) {
    const camp = porCampana.get(g.campanaId);
    if (!camp) continue;
    const nodo = nuevoNodo(`${g.campanaId}|${g.nombre}`, g.nombre, 4);
    sumar(nodo, g, null);
    camp.hijos.push(nodo);
  }
  const ordenar = (lista: Nodo[]) => {
    lista.sort((a, b) => b.coste - a.coste || (b.presDia ?? 0) - (a.presDia ?? 0));
    lista.forEach((n) => ordenar(n.hijos));
  };
  const raiz = [...clientes.values()];
  ordenar(raiz);
  if (ordenMarcas.length) raiz.sort((a, b) => ordenMarcas.indexOf(a.clave) - ordenMarcas.indexOf(b.clave));
  return raiz;
}

export interface FilaRotacion {
  campanaId: string;
  nombre: string;
  marca: string;
  ritmo: number;
  /** ARS por día: lo que le falta (topeadas) o lo que le sobra (ociosas) respecto de su presupuesto. */
  margenDia: number;
}

export interface Resumen {
  presDia: number;
  presMes: number;
  gasto: number;
  gastoDia: number;
  proyeccion: number;
  disponible: number;
  consumo: number | null;
  esperado: number;
  sobre: FilaRotacion[];
  sinGasto: FilaRotacion[];
  topeadas: FilaRotacion[];
  ociosas: FilaRotacion[];
  sobranteDia: number;
  impresiones: number;
  clics: number;
  conv: number;
}

/** Totales del mes y listas para rotar inversión (campañas topeadas vs. con presupuesto ocioso). */
export function resumir(campanas: CampanaGasto[], dias: number, diasMes: number): Resumen {
  let presDia = 0;
  let gasto = 0;
  let impresiones = 0;
  let clics = 0;
  let conv = 0;
  const sobre: FilaRotacion[] = [];
  const sinGasto: FilaRotacion[] = [];
  const topeadas: FilaRotacion[] = [];
  const ociosas: FilaRotacion[] = [];
  for (const c of campanas) {
    gasto += c.coste;
    impresiones += c.impresiones ?? 0;
    clics += c.clics;
    conv += c.conv;
    const pres = presupuestoActivo(c);
    if (pres === null) continue;
    presDia += pres;
    const r = ritmo(c.coste, pres, dias) ?? 0;
    const fila: FilaRotacion = { campanaId: c.id, nombre: c.nombre, marca: c.marca, ritmo: r, margenDia: pres - c.coste / Math.max(dias, 1) };
    if (c.coste <= 0) sinGasto.push(fila);
    else if (r > UMBRAL_SOBRE) sobre.push(fila);
    if (r >= UMBRAL_TOPE) topeadas.push(fila);
    else if (r < UMBRAL_OCIOSO) ociosas.push(fila);
  }
  const gastoDia = dias > 0 ? gasto / dias : 0;
  const presMes = presDia * diasMes;
  const porRitmo = (a: FilaRotacion, b: FilaRotacion) => b.ritmo - a.ritmo;
  ociosas.sort((a, b) => b.margenDia - a.margenDia);
  return {
    presDia,
    presMes,
    gasto,
    gastoDia,
    proyeccion: gastoDia * diasMes,
    disponible: Math.max(presMes - gasto, 0),
    consumo: presMes > 0 ? gasto / presMes : null,
    esperado: diasMes > 0 ? Math.min(dias / diasMes, 1) : 0,
    sobre: sobre.sort(porRitmo),
    sinGasto,
    topeadas: topeadas.sort(porRitmo),
    ociosas,
    sobranteDia: ociosas.reduce((s, f) => s + Math.max(f.margenDia, 0), 0),
    impresiones,
    clics,
    conv,
  };
}
