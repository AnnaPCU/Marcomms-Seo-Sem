import { describe, expect, it } from 'vitest';
import type { CambioAds } from '@/services/cambios';
import type { Evento, Recomendacion } from '@/services/recomendaciones';
import type { MetricaDia } from '@/services/metricas';
import {
  calcularImpacto, cruzarItem, fechaResultado, diasEntre, fechaArgentina, itemsDeTarjeta, juzgar, normalizarKeyword, normalizarTexto, sumarDias, sumarVentana,
  type ItemTarjeta, type Ventana,
} from './impacto';

const cambio = (over: Partial<CambioAds> & { detalle?: CambioAds['detalle'] }): CambioAds => ({
  id: Math.random().toString(36).slice(2), campanaId: 'c1', fecha: '2026-11-06T15:00:00', recurso: 'CAMPAIGN_CRITERION', operacion: 'CREATE',
  grupo: null, resumen: '', ...over, detalle: over.detalle ?? {},
});
const item = (over: Partial<ItemTarjeta>): ItemTarjeta => ({ paso: 1, tituloPaso: 'Paso', accion: 'agregar', tipo: 'negativa', texto: 'x', ...over });
const v = (over: Partial<Ventana>): Ventana => ({ desde: '2026-10-01', hasta: '2026-10-28', dias: 28, coste: 0, clics: 0, impresiones: 0, conversiones: 0, ...over });

describe('fechas', () => {
  it('suma y cuenta días', () => {
    expect(sumarDias('2026-10-31', 1)).toBe('2026-11-01');
    expect(sumarDias('2026-11-01', -28)).toBe('2026-10-04');
    expect(diasEntre('2026-10-31', '2026-11-08')).toBe(9);
  });
  it('pasa un instante UTC a la fecha de Argentina', () => {
    expect(fechaArgentina('2026-11-07T01:30:00Z')).toBe('2026-11-06');
    expect(fechaArgentina('2026-11-07T04:00:00+00:00')).toBe('2026-11-07');
  });
});

describe('normalizar', () => {
  it('keywords: sin tildes, corchetes ni comillas; conserva el +', () => {
    expect(normalizarKeyword('[Certificação  GMP+]')).toBe('certificacao gmp+');
    expect(normalizarKeyword('«canada gap»')).toBe('canada gap');
  });
  it('textos de anuncio: sin puntuación', () => {
    expect(normalizarTexto('Biodiésel al mercado de EE.UU.')).toBe(normalizarTexto('Biodiesel al mercado de EE. UU'));
  });
});

describe('cruzarItem', () => {
  const cambios = [
    cambio({ detalle: { texto: 'cargill', concordancia: 'amplia', negativa: true } }),
    cambio({ recurso: 'AD_GROUP_CRITERION', detalle: { texto: 'canada gap', concordancia: 'exacta', negativa: false, estado_despues: 'ENABLED' } }),
    cambio({ recurso: 'AD_GROUP_CRITERION', operacion: 'UPDATE', detalle: { texto: 'global gap', concordancia: 'amplia', negativa: false, estado_antes: 'ENABLED', estado_despues: 'PAUSED' } }),
    cambio({ recurso: 'AD', operacion: 'UPDATE', detalle: { titulos_agregados: ['Request a CanadaGAP Audit'], descripciones_agregadas: ['We certify CanadaGAP for fruit and vegetable growers, packers and brokers.'] } }),
    cambio({ recurso: 'AD', operacion: 'UPDATE', detalle: { urls_despues: ['https://argentina.controlunion.com/programa-de-certificacion/rspo/'] } }),
    cambio({ recurso: 'AD_GROUP', operacion: 'CREATE', grupo: 'FSC', detalle: { nombre: 'PEFC #2' } }),
    cambio({ recurso: 'AD_GROUP_CRITERION', detalle: { texto: 'soja epa', concordancia: 'frase', negativa: false } }),
  ];
  it('encuentra negativas, keywords nuevas y pausas', () => {
    expect(cruzarItem(item({ texto: 'cargill' }), cambios).estado).toBe('aplicado');
    expect(cruzarItem(item({ texto: 'indocert' }), cambios).estado).toBe('no_visto');
    expect(cruzarItem(item({ tipo: 'keyword', texto: '[canada gap]', concordancia: 'exacta' }), cambios).estado).toBe('aplicado');
    expect(cruzarItem(item({ tipo: 'keyword', accion: 'pausar', texto: 'global gap' }), cambios).estado).toBe('aplicado');
    // una negativa no cuenta como keyword nueva ni al revés
    expect(cruzarItem(item({ tipo: 'keyword', texto: 'cargill' }), cambios).estado).toBe('no_visto');
  });
  it('con la misma keyword en dos concordancias, cada ítem toma la suya', () => {
    const dos = [
      cambio({ recurso: 'AD_GROUP_CRITERION', detalle: { texto: 'certificação fsc', concordancia: 'exacta', negativa: false } }),
      cambio({ recurso: 'AD_GROUP_CRITERION', detalle: { texto: 'certificação fsc', concordancia: 'frase', negativa: false } }),
    ];
    const r = cruzarItem(item({ tipo: 'keyword', texto: 'certificação fsc', concordancia: 'frase' }), dos);
    expect(r.cambio?.detalle.concordancia).toBe('frase');
    expect(r.nota).toBeUndefined();
  });
  it('avisa cuando la concordancia cargada no es la propuesta', () => {
    const r = cruzarItem(item({ tipo: 'keyword', texto: 'canada gap', concordancia: 'frase' }), cambios);
    expect(r.estado).toBe('aplicado');
    expect(r.nota).toMatch(/exacta/);
  });
  it('títulos, descripciones y URL de anuncio', () => {
    expect(cruzarItem(item({ tipo: 'titulo', accion: 'reemplazar', texto: 'Request a CanadaGAP Audit' }), cambios).estado).toBe('aplicado');
    expect(cruzarItem(item({ tipo: 'descripcion', texto: 'We certify CanadaGAP for fruit and vegetable growers, packers and brokers' }), cambios).estado).toBe('aplicado');
    expect(cruzarItem(item({ tipo: 'titulo', texto: 'Otro título' }), cambios).estado).toBe('no_visto');
    expect(cruzarItem(item({ tipo: 'texto', accion: 'reemplazar', texto: 'https://argentina.controlunion.com/programa-de-certificacion/rspo' }), cambios).estado).toBe('aplicado');
  });
  it('grupo nuevo por nombre actual', () => {
    expect(cruzarItem(item({ tipo: 'grupo', accion: 'crear', texto: 'FSC' }), cambios).estado).toBe('aplicado');
  });
  it('las decisiones y los ajustes de configuración quedan a criterio salvo que se vean cargados', () => {
    expect(cruzarItem(item({ tipo: 'texto', accion: 'decidir', texto: '¿Certifica ganadería?' }), cambios).estado).toBe('a_criterio');
    expect(cruzarItem(item({ tipo: 'texto', accion: 'cambiar', texto: 'Límite de CPC: ARS 12.000' }), cambios).estado).toBe('a_criterio');
    expect(cruzarItem(item({ tipo: 'keyword', accion: 'decidir', texto: 'soja epa' }), cambios).estado).toBe('aplicado');
    expect(cruzarItem(item({ tipo: 'negativa', accion: 'decidir', texto: 'ecocert' }), cambios).estado).toBe('a_criterio');
  });
});

describe('ventanas y veredicto', () => {
  const met = (fecha: string, coste: number, clics: number, impresiones: number, conversiones = 0): MetricaDia =>
    ({ campanaId: 'c1', fecha, coste, clics, impresiones, conversiones });
  it('suma solo la campaña y el rango; los días sin fila cuentan como cero', () => {
    const m = [met('2026-10-01', 100, 1, 10), met('2026-10-03', 50, 1, 10), { ...met('2026-10-02', 999, 9, 99), campanaId: 'otra' }];
    expect(sumarVentana(m, 'c1', '2026-10-01', '2026-10-03')).toMatchObject({ dias: 3, coste: 150, clics: 2, impresiones: 20 });
  });
  it('menos de 14 días después: midiendo', () => {
    expect(juzgar(v({ clics: 20, impresiones: 400 }), v({ dias: 2, clics: 3, impresiones: 30 })).veredicto).toBe('midiendo');
  });
  it('CTR arriba y CPC abajo: positivo', () => {
    const j = juzgar(v({ coste: 28000, clics: 28, impresiones: 1400 }), v({ dias: 20, coste: 8000, clics: 16, impresiones: 400 }));
    expect(j.veredicto).toBe('positivo');
    expect(j.razones.join(' ')).toMatch(/CTR \+/);
  });
  it('CTR abajo y CPC arriba: negativo', () => {
    expect(juzgar(v({ coste: 28000, clics: 28, impresiones: 560 }), v({ dias: 20, coste: 20000, clics: 10, impresiones: 400 })).veredicto).toBe('negativo');
  });
  it('las conversiones pesan doble', () => {
    // CTR −20% pero pasa de 0 a 2 conversiones
    expect(juzgar(v({ coste: 28000, clics: 28, impresiones: 560 }), v({ dias: 20, coste: 10000, clics: 10, impresiones: 250, conversiones: 2 })).veredicto).toBe('positivo');
  });
  it('señal débil con pocos clics', () => {
    expect(juzgar(v({ coste: 5000, clics: 4, impresiones: 100 }), v({ dias: 9, coste: 3000, clics: 4, impresiones: 50 })).senalDebil).toBe(true);
  });
});

describe('calcularImpacto', () => {
  const rec = (over: Partial<Recomendacion>): Recomendacion => ({
    id: 'r1', clave: 'k', marca: 'CU', tipo: 'SEM', campanaId: 'c1', grupoId: null, sitio: null, pagina: null, titulo: 'Canada Gap', detalle: '',
    evidencia: { ficha: 'campana', pasos: [{ titulo: 'Negativas', items: [
      { accion: 'agregar', tipo: 'negativa', texto: 'cargill', concordancia: 'amplia' },
      { accion: 'agregar', tipo: 'negativa', texto: 'indocert', concordancia: 'amplia' },
      { accion: 'decidir', tipo: 'texto', texto: '¿Subir el presupuesto?' },
    ] }] },
    prioridad: 'media', estado: 'hecha', mesAlta: '2026-10', mesCierre: '2026-11', motivoDescarte: null, verificadaApi: false, verificadaEn: null,
    origen: null, orden: 0, actualizadaPor: null, updatedAt: '2026-11-06T20:00:00Z', ...over,
  });
  const ev = (aEstado: string, creadoEn: string): Evento => ({ id: aEstado + creadoEn, recomendacionId: 'r1', deEstado: null, aEstado, motivo: null, usuario: null, creadoEn });
  const metricas: MetricaDia[] = [];
  for (let d = 0; d < 50; d++) {
    const f = sumarDias('2026-10-01', d);
    metricas.push({ campanaId: 'c1', fecha: f, coste: 1000, clics: f < '2026-10-30' ? 1 : 2, impresiones: 20, conversiones: 0 });
  }
  const r = calcularImpacto({
    recs: [rec({}), rec({ id: 'r2', estado: 'propuesta' }), rec({ id: 'r3', campanaId: null })],
    eventos: [ev('en_proceso', '2026-10-28T13:00:00Z'), ev('hecha', '2026-11-06T20:00:00Z')],
    cambios: [cambio({ fecha: '2026-10-29T10:00:00', detalle: { texto: 'cargill', concordancia: 'amplia', negativa: true } }),
      cambio({ fecha: '2026-10-29T10:05:00', recurso: 'CAMPAIGN_BUDGET', operacion: 'UPDATE', detalle: {}, resumen: 'Otro cambio' })],
    metricas,
  });
  it('solo SEM hechas con campaña', () => {
    expect(r.map((x) => x.rec.id)).toEqual(['r1']);
  });
  it('cuenta los ítems aplicados sobre los verificables y separa los otros cambios', () => {
    expect(r[0].aplicados).toBe(1);
    expect(r[0].verificables).toBe(2);
    expect(r[0].otrosCambios).toHaveLength(1);
  });
  it('mide desde la fecha real del cambio, no desde el día en que se movió la tarjeta', () => {
    expect(r[0].primerCambio).toBe('2026-10-29');
    expect(r[0].antes).toMatchObject({ desde: '2026-10-01', hasta: '2026-10-28', dias: 28 });
    expect(r[0].despues).toMatchObject({ desde: '2026-10-30', hasta: '2026-11-19', dias: 21 });
    expect(fechaResultado(r[0])).toBe('2026-11-12');
    expect(r[0].juicio.veredicto).toBe('positivo');
    expect(r[0].avisos.some((a) => a.includes('presupuesto'))).toBe(true);
  });
  it('itemsDeTarjeta ignora ítems sin texto', () => {
    expect(itemsDeTarjeta({ evidencia: { pasos: [{ items: [{ texto: '' }, { texto: 'a', accion: 'agregar', tipo: 'negativa' }] }] } })).toHaveLength(1);
  });
});
