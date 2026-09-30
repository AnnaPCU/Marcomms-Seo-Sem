/**
 * Hooks de datos, uno por recurso. Cada uno expone { datos, cargando, error, recargar }.
 * Las recomendaciones además se refrescan solas por realtime.
 */
import { useCallback, useEffect, useMemo, useState } from 'react';
import type { Tipo } from '@/lib/database.types';
import { listarRecomendaciones, suscribirRecomendaciones, type Recomendacion } from '@/services/recomendaciones';
import { listarCampanas, listarGrupos, type Campana, type Grupo } from '@/services/campanas';
import { ultimasExtracciones, type Extraccion } from '@/services/extracciones';
import { listarMetricas, listarMetricasGrupo, type MetricaGrupoMes, type MetricaMes } from '@/services/metricas';

interface Estado<T> {
  datos: T;
  cargando: boolean;
  error: string | null;
  recargar: () => void;
}

function useCarga<T>(inicial: T, cargar: () => Promise<T>): Estado<T> {
  const [datos, setDatos] = useState<T>(inicial);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);
  const recargar = useCallback(() => {
    setCargando(true);
    setTick((t) => t + 1);
  }, []);

  useEffect(() => {
    let vivo = true;
    cargar()
      .then((d) => {
        if (vivo) {
          setDatos(d);
          setError(null);
        }
      })
      .catch((e: unknown) => {
        if (vivo) setError(e instanceof Error ? e.message : String(e));
      })
      .finally(() => {
        if (vivo) setCargando(false);
      });
    return () => {
      vivo = false;
    };
  }, [cargar, tick]);

  return { datos, cargando, error, recargar };
}

const VACIO_REC: Recomendacion[] = [];
const VACIO_CAMP: Campana[] = [];
const VACIO_GRU: Grupo[] = [];
const VACIO_MET: MetricaMes[] = [];
const VACIO_MET_G: MetricaGrupoMes[] = [];
const VACIO_EXT: Record<'search_console' | 'google_ads', Extraccion | null> = { search_console: null, google_ads: null };

export function useRecomendaciones(tipo?: Tipo) {
  const cargar = useCallback(() => listarRecomendaciones(tipo), [tipo]);
  const estado = useCarga(VACIO_REC, cargar);
  const { recargar } = estado;
  useEffect(() => suscribirRecomendaciones(recargar), [recargar]);

  // Actualización optimista: mover una tarjeta se ve al instante; cuando llega una lista nueva de la base
  // (realtime o recarga) la copia local se descarta sola porque quedó atada a la lista anterior.
  const [locales, setLocales] = useState<{ base: Recomendacion[]; lista: Recomendacion[] } | null>(null);
  const datos = locales && locales.base === estado.datos ? locales.lista : estado.datos;
  const aplicarLocal = useCallback(
    (fn: (prev: Recomendacion[]) => Recomendacion[]) =>
      setLocales((prev) => {
        const actual = prev && prev.base === estado.datos ? prev.lista : estado.datos;
        return { base: estado.datos, lista: fn(actual) };
      }),
    [estado.datos],
  );
  return { ...estado, datos, aplicarLocal };
}

export function useCampanas() {
  const cargar = useCallback(() => listarCampanas(), []);
  return useCarga(VACIO_CAMP, cargar);
}

export function useGrupos() {
  const cargar = useCallback(() => listarGrupos(), []);
  return useCarga(VACIO_GRU, cargar);
}

export function useExtracciones() {
  const cargar = useCallback(() => ultimasExtracciones(), []);
  return useCarga(VACIO_EXT, cargar);
}

export function useMetricas() {
  const cargar = useCallback(() => listarMetricas(), []);
  return useCarga(VACIO_MET, cargar);
}

export function useMetricasGrupo() {
  const cargar = useCallback(() => listarMetricasGrupo(), []);
  return useCarga(VACIO_MET_G, cargar);
}

/** Índices por id para resolver nombres de campaña y grupo desde una tarjeta. */
export function useCatalogo() {
  const campanas = useCampanas();
  const grupos = useGrupos();
  const porId = useMemo(() => {
    const c = new Map(campanas.datos.map((x) => [x.id, x]));
    const g = new Map(grupos.datos.map((x) => [x.id, x]));
    return { campana: (id: string | null) => (id ? c.get(id) ?? null : null), grupo: (id: string | null) => (id ? g.get(id) ?? null : null) };
  }, [campanas.datos, grupos.datos]);
  return { campanas: campanas.datos, grupos: grupos.datos, cargando: campanas.cargando || grupos.cargando, ...porId };
}
