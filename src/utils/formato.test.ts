import { describe, expect, it } from 'vitest';
import { ars, campanaCorta, diasDesde, entero, mesActual, mesCorto, pct } from './formato';

describe('formato', () => {
  it('ars redondea y separa miles', () => {
    expect(ars(2251937.4)).toBe('ARS 2.251.937');
    expect(ars(null)).toBe('—');
  });
  it('entero y pct', () => {
    expect(entero(1177)).toBe('1.177');
    expect(pct(458291, 2251937)).toBe('20%');
    expect(pct(1, 0)).toBe('—');
  });
  it('mesCorto y mesActual', () => {
    expect(mesCorto('2026-09')).toMatch(/sep/i);
    expect(mesActual(new Date(2026, 8, 28))).toBe('2026-09');
  });
  it('diasDesde', () => {
    expect(diasDesde('2026-09-14T00:00:00Z', new Date('2026-09-28T00:00:00Z'))).toBe(14);
    expect(diasDesde(null)).toBeNull();
  });
  it('campanaCorta quita el sufijo Search', () => {
    expect(campanaCorta('CU España - IFS - Search')).toBe('CU España - IFS');
    expect(campanaCorta('CU Canada- Aqua / Fisheries')).toBe('CU Canada- Aqua / Fisheries');
  });
});
