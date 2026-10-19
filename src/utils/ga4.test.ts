import { describe, expect, it } from 'vitest';
import type { Ga4Datos } from '@/services/ga4';
import { alertas, clicsAds, serieSitios, tramosCanal, totales } from './ga4';

const d = (over: Partial<Ga4Datos>): Ga4Datos => ({
  sesiones: 1000, interaccion: 500, usuarios: 800, vistas: 2000, duracion_media: 90, canales: {}, contactos: {}, contactos_total: 3,
  directo_sin_interaccion: 0, landings_pagas: [], landings_organicas: [], ...over,
});

describe('ga4', () => {
  it('canales en orden fijo, sin los vacíos y con el resto en «Otros»', () => {
    const t = tramosCanal(d({ canales: { Direct: { sesiones: 5, interaccion: 1 }, 'Organic Search': { sesiones: 9, interaccion: 6 }, Unassigned: { sesiones: 2, interaccion: 0 }, 'Cross-network': { sesiones: 1, interaccion: 1 } } }));
    expect(t.map((x) => x.id)).toEqual(['Organic Search', 'Direct', 'otros']);
    expect(t[2].sesiones).toBe(3);
  });

  it('clics de Ads por sitio: suma CU + PCU del país, null sin campañas o sin gasto del mes', () => {
    const campanas = [
      { id: 'a', marca: 'CU' as const, unidad: 'España' },
      { id: 'b', marca: 'PCU' as const, unidad: 'España' },
      { id: 'c', marca: 'CU' as const, unidad: 'Portugal' },
    ];
    const met = [
      { campanaId: 'a', mes: '2026-09', clics: 100 },
      { campanaId: 'b', mes: '2026-09', clics: 50 },
      { campanaId: 'c', mes: '2026-09', clics: 7 },
    ];
    expect(clicsAds('espana.controlunion.com', '2026-09', campanas, met)).toBe(150);
    expect(clicsAds('espana.controlunion.com', '2026-10', campanas, met)).toBeNull();
    expect(clicsAds('peru.controlunion.com', '2026-09', campanas, met)).toBeNull();
  });

  it('alerta de medición cuando GA4 ve menos de 3 de cada 4 clics', () => {
    const pago = (s: number) => d({ canales: { 'Paid Search': { sesiones: s, interaccion: s / 2 } }, contactos: { 'Paid Search': { formularios: 1, emails: 0 } } });
    expect(alertas(pago(386), 606).map((a) => a.clave)).toContain('medicion');
    expect(alertas(pago(124), 133).map((a) => a.clave)).not.toContain('medicion');
    expect(alertas(pago(10), 20).map((a) => a.clave)).not.toContain('medicion'); // muy pocos clics para juzgar
    expect(alertas(pago(10), null).map((a) => a.clave)).not.toContain('medicion');
  });

  it('bots, landings flojas y falta de contactos', () => {
    const a = alertas(
      d({
        directo_sin_interaccion: 600,
        contactos_total: 0,
        canales: { 'Paid Search': { sesiones: 80, interaccion: 30 } },
        landings_pagas: [
          { pagina: '/iso-27001', sesiones: 40, interaccion: 12 },
          { pagina: '/buena', sesiones: 40, interaccion: 30 },
          { pagina: '(not set)', sesiones: 30, interaccion: 0 },
          { pagina: '/chica', sesiones: 5, interaccion: 0 },
        ],
      }),
      null,
    ).map((x) => x.clave);
    expect(a).toEqual(['bots', 'landing:/iso-27001', 'pago-sin-contactos']);
  });

  it('totales', () => {
    expect(totales([d({ canales: { 'Organic Search': { sesiones: 10, interaccion: 5 } } }), d({})])).toEqual({ sesiones: 2000, interaccion: 1000, contactos: 6, organico: 10 });
  });

  it('serie por mes de varios sitios, con las visitas reales por canal', () => {
    const s = serieSitios([
      { mes: '2026-10', dias: 18, datos: d({ canales: { 'Organic Search': { sesiones: 10, interaccion: 6 } } }) },
      { mes: '2026-09', dias: 30, datos: d({ canales: { 'Organic Search': { sesiones: 10, interaccion: 5 }, Unassigned: { sesiones: 4, interaccion: 1 } } }) },
      { mes: '2026-09', dias: 30, datos: d({ contactos_total: 7 }) },
    ]);
    expect(s.map((x) => [x.mes, x.dias, x.diasMes, x.sesiones, x.contactos])).toEqual([
      ['2026-09', 30, 30, 2000, 10],
      ['2026-10', 18, 31, 1000, 3],
    ]);
    expect(s[0].canales).toEqual({ 'Organic Search': 5, otros: 1 });
  });
});
