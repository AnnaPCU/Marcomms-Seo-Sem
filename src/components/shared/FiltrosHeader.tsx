/** Pone los filtros de la vista en la segunda fila del encabezado, en vez de una barra dentro de la página. */
import { useContext, type ReactNode } from 'react';
import { createPortal } from 'react-dom';
import { RanuraFiltros } from './ranura';

export default function FiltrosHeader({ children }: { children: ReactNode }) {
  const ranura = useContext(RanuraFiltros);
  return ranura ? createPortal(children, ranura) : null;
}
