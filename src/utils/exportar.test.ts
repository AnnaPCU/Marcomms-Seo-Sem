import { describe, expect, it } from 'vitest';
import type { Recomendacion } from '@/services/recomendaciones';
import { aCelda, clavesEvidencia, hojaHistorial, hojaLeeme, hojaTareas, nombreArchivo, type ContextoExport } from './exportar';

const rec = (over: Partial<Recomendacion>): Recomendacion => ({
  id: 'r1', clave: 'sem-cu-espana-ifs', marca: 'CU', tipo: 'SEM', campanaId: 'c1', grupoId: 'g1', sitio: null, pagina: null,
  titulo: 'IFS: reescribir anuncio', detalle: 'Detalle largo', evidencia: {}, prioridad: 'alta', estado: 'propuesta', mesAlta: '2026-09',
  mesCierre: null, motivoDescarte: null, verificadaApi: false, verificadaEn: null, origen: 'plan', orden: 2, actualizadaPor: null,
  updatedAt: '2026-10-01T12:00:00Z', ...over,
});
const ctx: ContextoExport = {
  vista: 'SEM · campañas',
  filtros: [{ etiqueta: 'Cliente', valor: 'Control Union' }],
  campana: () => 'CU España - IFS - SEARCH',
  grupo: () => 'Food Safety',
  pais: () => 'España',
  ahora: new Date('2026-10-21T10:00:00'),
};

describe('exportar', () => {
  it('celdas: listas una por línea, objetos como clave: valor, sin perder datos', () => {
    expect(aCelda(['a', 'b'])).toBe('a\nb');
    expect(aCelda([{ termino: 'iscc', coste: 23310 }])).toBe('termino: iscc · coste: 23310');
    expect(aCelda([])).toBeNull();
    expect(aCelda(null)).toBeNull();
    expect(aCelda(93875)).toBe(93875);
    expect(aCelda({ a: 1 })).toBe('{"a":1}');
    expect(String(aCelda('x'.repeat(40000))).length).toBeLessThan(32767);
  });

  it('columnas de evidencia: las conocidas en orden, las nuevas al final, sin «acciones»', () => {
    const c = clavesEvidencia([rec({ evidencia: { zeta: 1, diagnostico: 'd', ficha: 'anuncio', acciones: ['anuncio'] } })]);
    expect(c.map(([k]) => k)).toEqual(['ficha', 'diagnostico', 'zeta']);
  });

  it('hoja de tareas: una fila por tarjeta con todos los campos y el JSON completo', () => {
    const h = hojaTareas(
      [
        rec({ id: 'r2', estado: 'hecha', evidencia: { ficha: 'plan' } }),
        rec({ evidencia: { ficha: 'anuncio', acciones: ['anuncio', 'negativas'], titulos_propuestos: ['T1', 'T2'] } }),
      ],
      ctx,
    );
    expect(h.encabezado).toContain('Detalle');
    expect(h.encabezado).toContain('Títulos propuestos');
    expect(h.encabezado.at(-1)).toBe('Evidencia completa (JSON)');
    expect(h.filas).toHaveLength(2);
    const fila = Object.fromEntries(h.encabezado.map((c, i) => [c, h.filas[0][i]]));
    expect(fila).toMatchObject({ Estado: 'Propuesta', Cliente: 'Control Union', País: 'España', 'Títulos propuestos': 'T1\nT2', 'Tipo de mejora': 'Anuncio (títulos y descripciones), Negativas' });
    expect(JSON.parse(String(fila['Evidencia completa (JSON)'])).titulos_propuestos).toEqual(['T1', 'T2']);
    expect(h.anchos).toHaveLength(h.encabezado.length);
  });

  it('historial solo de las tarjetas exportadas, en orden', () => {
    const h = hojaHistorial(
      [rec({})],
      [
        { id: 'e2', recomendacionId: 'r1', deEstado: 'propuesta', aEstado: 'en_proceso', motivo: null, usuario: 'Equipo', creadoEn: '2026-10-02T10:00:00Z' },
        { id: 'e1', recomendacionId: 'r1', deEstado: null, aEstado: 'propuesta', motivo: null, usuario: null, creadoEn: '2026-09-30T10:00:00Z' },
        { id: 'e3', recomendacionId: 'otra', deEstado: null, aEstado: 'hecha', motivo: null, usuario: null, creadoEn: '2026-10-03T10:00:00Z' },
      ],
    );
    expect(h.filas.map((f) => f[4])).toEqual(['Propuesta', 'En proceso']);
  });

  it('léeme con filtros y conteos', () => {
    const h = hojaLeeme([rec({}), rec({ estado: 'hecha' })], 3, ctx);
    expect(h.filas.find((f) => f[0] === 'Filtros aplicados')?.[1]).toBe('Cliente: Control Union');
    expect(h.filas.find((f) => f[0] === 'Tarjetas')?.[1]).toBe(2);
  });

  it('nombre de archivo', () => {
    expect(nombreArchivo('SEM', ['CU', 'España', ''], new Date('2026-10-21T10:00:00'))).toBe('SEM_CU_España_2026-10-21.xlsx');
  });
});
