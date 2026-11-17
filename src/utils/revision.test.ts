import { describe, expect, it } from 'vitest';
import { actualizacionReciente } from './revision';

const hoy = new Date('2026-12-10T12:00:00');

describe('actualizacionReciente', () => {
  it('devuelve el último ajuste si tiene menos de 35 días', () => {
    const ev = { revisiones: [{ mes: '2026-11', accion: 'alta' }, { mes: '2026-12', accion: 'ajuste', motivo: 'nuevos términos', fecha: '2026-12-04' }] };
    expect(actualizacionReciente(ev, hoy)?.motivo).toBe('nuevos términos');
  });
  it('ignora ajustes viejos y entradas que no son ajuste', () => {
    expect(actualizacionReciente({ revisiones: [{ mes: '2026-10', accion: 'ajuste', fecha: '2026-10-04' }] }, hoy)).toBeNull();
    expect(actualizacionReciente({ revisiones: [{ mes: '2026-12', accion: 'verificada', fecha: '2026-12-04' }] }, hoy)).toBeNull();
    expect(actualizacionReciente({}, hoy)).toBeNull();
  });
  it('sin fecha, cuenta solo el ajuste del mes actual', () => {
    expect(actualizacionReciente({ revisiones: [{ mes: '2026-12', accion: 'ajuste' }] }, hoy)).not.toBeNull();
    expect(actualizacionReciente({ revisiones: [{ mes: '2026-11', accion: 'ajuste' }] }, hoy)).toBeNull();
  });
});
