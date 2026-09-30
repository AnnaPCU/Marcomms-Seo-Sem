import { describe, expect, it } from 'vitest';
import { armarArbol, consumoMes, diasDelMes, presupuestoActivo, resumir, ritmo, semaforo, type CampanaGasto } from './presupuesto';

const c = (id: string, over: Partial<CampanaGasto>): CampanaGasto => ({
  id, nombre: id, marca: 'CU', unidad: 'España', estado: 'ENABLED', presupuestoDia: 1000, coste: 0, clics: 0, conv: 0, ...over,
});

describe('presupuesto', () => {
  it('solo cuenta el presupuesto de campañas activas', () => {
    expect(presupuestoActivo({ estado: 'ENABLED', presupuestoDia: 500 })).toBe(500);
    expect(presupuestoActivo({ estado: 'REMOVED', presupuestoDia: 500 })).toBeNull();
    expect(presupuestoActivo({ estado: 'ENABLED', presupuestoDia: 0 })).toBeNull();
  });

  it('ritmo, consumo y días del mes', () => {
    expect(ritmo(29000, 1000, 29)).toBe(1);
    expect(consumoMes(15000, 1000, 30)).toBe(0.5);
    expect(diasDelMes('2026-09')).toBe(30);
    expect(diasDelMes('2026-10')).toBe(31);
  });

  it('semáforo: rojo sobre 105% o sin gasto, verde en el medio, gris sin presupuesto', () => {
    expect(semaforo(0, 1000, 29)).toBe('rojo');
    expect(semaforo(31000, 1000, 29)).toBe('rojo'); // 107%
    expect(semaforo(29000, 1000, 29)).toBe('verde'); // 100%
    expect(semaforo(3000, 1000, 29)).toBe('verde'); // 10%
    expect(semaforo(5000, null, 29)).toBe('gris');
  });

  it('árbol cliente → país → campaña → grupo con totales', () => {
    const arbol = armarArbol(
      [c('a', { coste: 100 }), c('b', { coste: 300, unidad: 'Portugal' }), c('x', { marca: 'PS', unidad: 'Argentina', coste: 50, estado: 'PAUSED' })],
      [{ campanaId: 'a', nombre: 'G1', coste: 60, clics: 1, conv: 0 }, { campanaId: 'a', nombre: 'G2', coste: 40, clics: 0, conv: 0 }],
      ['CU', 'PS'],
    );
    expect(arbol.map((n) => n.clave)).toEqual(['CU', 'PS']);
    expect(arbol[0].coste).toBe(400);
    expect(arbol[0].presDia).toBe(2000);
    expect(arbol[0].hijos[0].nombre).toBe('Portugal'); // ordenado por gasto
    expect(arbol[1].presDia).toBeNull(); // campaña pausada: su presupuesto no cuenta
    const a = arbol[0].hijos[1].hijos[0];
    expect(a.hijos.map((g) => g.nombre)).toEqual(['G1', 'G2']);
  });

  it('resumen para rotar inversión', () => {
    const r = resumir(
      [c('tope', { coste: 30000 }), c('ocio', { coste: 5000 }), c('cero', { coste: 0 }), c('elim', { estado: 'REMOVED', coste: 0 })],
      29,
      30,
    );
    expect(r.presDia).toBe(3000);
    expect(r.presMes).toBe(90000);
    expect(r.topeadas.map((f) => f.campanaId)).toEqual(['tope']);
    expect(r.ociosas.map((f) => f.campanaId)).toEqual(['cero', 'ocio']);
    expect(r.sinGasto.map((f) => f.campanaId)).toEqual(['cero']);
    expect(r.sobre.map((f) => f.campanaId)).toEqual([]); // 103%: topeada pero no por encima del 5%
    expect(Math.round(r.sobranteDia)).toBe(1828);
  });
});
