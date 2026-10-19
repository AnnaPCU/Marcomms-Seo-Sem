import { describe, expect, it } from 'vitest';
import type { MetricaMes } from '@/services/metricas';
import { cpc, matriz, mesPorDefecto, rangoMeses, serieMensual, variacion } from './historico';

const m = (campanaId: string, mes: string, coste: number, clics = 0, over: Partial<MetricaMes> = {}): MetricaMes => ({
  campanaId, mes, desde: `${mes}-01`, hasta: null, dias: null, coste, clics, impresiones: clics * 10, conversiones: 0,
  monedaOriginal: null, costeOriginal: null, tipoCambio: null, ...over,
});
const campanas = [
  { id: 'a', nombre: 'CU España - GMP+ - Search', marca: 'CU', unidad: 'España', cuenta: 'anterior' },
  { id: 'b', nombre: 'CU España - GMP+ - Search', marca: 'CU', unidad: 'España', cuenta: 'actual' },
  { id: 'c', nombre: 'PS Argentina - Bio - Search', marca: 'PS', unidad: 'Argentina', cuenta: 'actual' },
];

describe('historico', () => {
  it('rango de meses cruza el año', () => {
    expect(rangoMeses('2025-11', '2026-02')).toEqual(['2025-11', '2025-12', '2026-01', '2026-02']);
  });

  it('serie mensual sin huecos, con el gasto en euros separado y el mes parcial', () => {
    const s = serieMensual(campanas, [
      m('a', '2026-02', 100, 10, { monedaOriginal: 'EUR', costeOriginal: 0.06, tipoCambio: 1665 }),
      m('b', '2026-04', 300, 30),
      m('c', '2026-04', 50, 5, { dias: 18 }),
    ]);
    expect(s.map((x) => x.mes)).toEqual(['2026-02', '2026-03', '2026-04']);
    expect(s[0]).toMatchObject({ coste: 100, costeEur: 100, campanas: 1 });
    expect(s[1]).toMatchObject({ coste: 0, campanas: 0 });
    expect(s[2]).toMatchObject({ coste: 350, clics: 35, campanas: 2, dias: 30, porMarca: { CU: 300, PS: 50 } });
  });

  it('el filtro de campañas se respeta', () => {
    expect(serieMensual([campanas[2]], [m('a', '2026-02', 100), m('c', '2026-04', 50)]).map((x) => x.coste)).toEqual([50]);
  });

  it('matriz cliente → país → campaña: las dos cuentas quedan como campañas distintas', () => {
    const t = matriz(campanas, [m('a', '2026-06', 100), m('b', '2026-08', 300), m('c', '2026-08', 50)], ['CU', 'PS']);
    expect(t.map((f) => f.clave)).toEqual(['CU', 'PS']);
    const espana = t[0].hijos[0];
    expect(espana.hijos.map((f) => [f.clave, f.cuenta])).toEqual([['b', 'actual'], ['a', 'anterior']]);
    expect(espana.porMes.get('2026-06')?.coste).toBe(100);
    expect(t[0].total.coste).toBe(400);
  });

  it('indicadores y variación', () => {
    expect(cpc({ coste: 100, clics: 4, impresiones: 0, conv: 0 })).toBe(25);
    expect(cpc({ coste: 100, clics: 0, impresiones: 0, conv: 0 })).toBeNull();
    expect(variacion(150, 100)).toBeCloseTo(0.5);
    expect(variacion(150, 0)).toBeNull();
  });

  it('por defecto, el último mes cerrado', () => {
    expect(mesPorDefecto(['2026-08', '2026-10', '2026-09'], '2026-10')).toBe('2026-09');
    expect(mesPorDefecto(['2026-10'], '2026-10')).toBe('2026-10');
    expect(mesPorDefecto([], '2026-10')).toBe('');
  });
});
