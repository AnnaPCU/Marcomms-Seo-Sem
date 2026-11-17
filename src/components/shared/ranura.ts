import { createContext } from 'react';

/** Lugar del encabezado (segunda fila, a la izquierda de «Datos reales») donde cada vista pone sus filtros. */
export const RanuraFiltros = createContext<HTMLElement | null>(null);
