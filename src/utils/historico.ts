/**
 * Vista «Histórico» del presupuesto: la serie mes a mes y la matriz cliente → país → campaña × mes.
 * Sin dependencias de React; se testea en historico.test.ts.
 */
import type { MetricaMes } from '@/services/metricas';

export interface CampanaRef {
  id: string;
  nombre: string;
  marca: string;
  unidad: string;
  cuenta?: string;
}

export interface Totales {
  coste: number;
  clics: number;
  impresiones: number;
  conv: number;
}

export interface MesSerie extends Totales {
  mes: string;
  /** Campañas con gasto o impresiones en el mes. */
  campanas: number;
  /** Días con datos y días del mes: el mes en curso queda parcial. */
  dias: number;
  diasMes: number;
  /** Parte del gasto que vino de la cuenta en euros (ya en pesos). */
  costeEur: number;
  /** Gasto por marca, para la barra apilada. */
  porMarca: Record<string, number>;
}

const cero = (): Totales => ({ coste: 0, clics: 0, impresiones: 0, conv: 0 });
const sumar = (a: Totales, m: MetricaMes) => {
  a.coste += m.coste;
  a.clics += m.clics;
  a.impresiones += m.impresiones;
  a.conv += m.conversiones;
};

export const diasDe = (mes: string) => {
  const [a, m] = mes.split('-').map(Number);
  return new Date(a, m, 0).getDate();
};

/** Meses de `desde` a `hasta` inclusive, en orden ('AAAA-MM'). */
export function rangoMeses(desde: string, hasta: string): string[] {
  const out: string[] = [];
  let [a, m] = desde.split('-').map(Number);
  const [a2, m2] = hasta.split('-').map(Number);
  while (a < a2 || (a === a2 && m <= m2)) {
    out.push(`${a}-${String(m).padStart(2, '0')}`);
    m += 1;
    if (m > 12) {
      a += 1;
      m = 1;
    }
  }
  return out;
}

/** Serie mensual de las campañas visibles, del primer al último mes con datos (sin huecos). */
export function serieMensual(campanas: CampanaRef[], metricas: MetricaMes[]): MesSerie[] {
  const porId = new Map(campanas.map((c) => [c.id, c]));
  const propias = metricas.filter((m) => porId.has(m.campanaId));
  if (!propias.length) return [];
  const meses = propias.map((m) => m.mes).sort();
  const serie = new Map<string, MesSerie>(
    rangoMeses(meses[0], meses[meses.length - 1]).map((mes) => [
      mes,
      { mes, ...cero(), campanas: 0, dias: 0, diasMes: diasDe(mes), costeEur: 0, porMarca: {} },
    ]),
  );
  for (const m of propias) {
    const s = serie.get(m.mes)!;
    const c = porId.get(m.campanaId)!;
    sumar(s, m);
    if (m.coste > 0 || m.impresiones > 0) s.campanas += 1;
    s.dias = Math.max(s.dias, m.dias ?? s.diasMes);
    if (m.monedaOriginal) s.costeEur += m.coste;
    s.porMarca[c.marca] = (s.porMarca[c.marca] ?? 0) + m.coste;
  }
  return [...serie.values()];
}

export const cpc = (t: Totales) => (t.clics ? t.coste / t.clics : null);
export const ctr = (t: Totales) => (t.impresiones ? t.clics / t.impresiones : null);
export const costoConv = (t: Totales) => (t.conv ? t.coste / t.conv : null);

/** Variación contra el valor anterior; null si no hay base. */
export function variacion(actual: number | null, anterior: number | null): number | null {
  if (actual === null || anterior === null || anterior === 0) return null;
  return actual / anterior - 1;
}

export interface FilaMatriz {
  clave: string;
  nombre: string;
  nivel: 1 | 2 | 3;
  cuenta?: string;
  total: Totales;
  porMes: Map<string, Totales>;
  hijos: FilaMatriz[];
}

/** Cliente → país → campaña, con los totales de cada mes. Ordena por gasto total. */
export function matriz(campanas: CampanaRef[], metricas: MetricaMes[], ordenMarcas: string[] = []): FilaMatriz[] {
  const porId = new Map(campanas.map((c) => [c.id, c]));
  const nueva = (clave: string, nombre: string, nivel: FilaMatriz['nivel']): FilaMatriz => ({ clave, nombre, nivel, total: cero(), porMes: new Map(), hijos: [] });
  const clientes = new Map<string, FilaMatriz>();
  const filasCampana = new Map<string, FilaMatriz>();
  for (const m of metricas) {
    const c = porId.get(m.campanaId);
    if (!c) continue;
    let cli = clientes.get(c.marca);
    if (!cli) clientes.set(c.marca, (cli = nueva(c.marca, c.marca, 1)));
    let pais = cli.hijos.find((h) => h.nombre === c.unidad);
    if (!pais) cli.hijos.push((pais = nueva(`${c.marca}|${c.unidad}`, c.unidad, 2)));
    let camp = filasCampana.get(c.id);
    if (!camp) {
      camp = { ...nueva(c.id, c.nombre, 3), cuenta: c.cuenta };
      filasCampana.set(c.id, camp);
      pais.hijos.push(camp);
    }
    for (const f of [cli, pais, camp]) {
      sumar(f.total, m);
      if (!f.porMes.has(m.mes)) f.porMes.set(m.mes, cero());
      sumar(f.porMes.get(m.mes)!, m);
    }
  }
  const ordenar = (l: FilaMatriz[]) => {
    l.sort((a, b) => b.total.coste - a.total.coste);
    l.forEach((f) => ordenar(f.hijos));
  };
  const raiz = [...clientes.values()];
  ordenar(raiz);
  if (ordenMarcas.length) raiz.sort((a, b) => ordenMarcas.indexOf(a.clave) - ordenMarcas.indexOf(b.clave));
  return raiz;
}

/** Último mes cerrado con datos (el anterior al mes en curso); si no hay, el más reciente. */
export function mesPorDefecto(meses: string[], mesEnCurso: string): string {
  const orden = [...meses].sort().reverse();
  return orden.find((m) => m < mesEnCurso) ?? orden[0] ?? '';
}
