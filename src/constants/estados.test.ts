import { describe, expect, it } from 'vitest';
import { accionesDe } from './estados';

describe('accionesDe', () => {
  it('devuelve los tipos conocidos en el orden de ACCIONES', () => {
    expect(accionesDe({ acciones: ['negativas', 'anuncio', 'otra'] })).toEqual(['anuncio', 'negativas']);
  });
  it('tolera tarjetas sin tipos o con datos inválidos', () => {
    expect(accionesDe({})).toEqual([]);
    expect(accionesDe({ acciones: 'anuncio' })).toEqual([]);
  });
});
