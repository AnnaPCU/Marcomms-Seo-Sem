/**
 * «Cada 10 días»: el mes en tres tramos (1–10, 11–20, 21–fin). Para cada tramo, gasto contra el presupuesto de esos
 * días (si se pasó y por cuánto) y, al costado, cuánto del presupuesto del mes ya se consumió. Resumido: arriba los
 * totales de lo filtrado, abajo el mismo árbol cliente → país → campaña de la vista mensual (sin grupos: no tienen
 * gasto por día).
 */
import { ChevronRight } from 'lucide-react';
import { MARCA_BY_ID } from '@/constants/estados';
import { Tarjeta } from '@/components/shared/Ui';
import { ars, campanaCorta, compacto } from '@/utils/formato';
import { campanasDe, consumoMes, semaforo, type Decena, type Nodo } from '@/utils/presupuesto';
import { BarraConsumo, COLOR_SEMAFORO } from './Semaforo';

const COLS = 'grid grid-cols-[18px_minmax(0,1fr)_repeat(3,minmax(92px,120px))_minmax(130px,170px)] items-center gap-3';
const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];

interface Props {
  arbol: Nodo[];
  mes: string;
  diasMes: number;
  decenas: Decena[];
  gasto: Map<string, [number, number, number]>;
  abiertos: Set<string>;
  alternar: (k: string) => void;
}

const sumaTramo = (ids: string[], gasto: Props['gasto'], i: number) => ids.reduce((s, id) => s + (gasto.get(id)?.[i] ?? 0), 0);

/** Celda de un tramo: gasto y % del presupuesto de esos días, en verde (dentro) o rojo (se pasó más de 5% o no gastó). */
function Celda({ coste, presDia, d }: { coste: number; presDia: number | null; d: Decena }) {
  if (d.conDatos === 0) return <span className="text-right text-xs text-mc-grey">—</span>;
  const sem = semaforo(coste, presDia, d.conDatos);
  const pct = presDia ? coste / (presDia * d.conDatos) : null;
  return (
    <span className="text-right leading-tight">
      <span className="block font-mono text-[12.5px] text-mc-navy">{compacto(coste)}</span>
      <span className={`block font-mono text-[11px] font-semibold ${COLOR_SEMAFORO[sem].texto}`}>{pct === null ? '' : `${Math.round(pct * 100)}%`}</span>
    </span>
  );
}

function Fila({ n, props, transcurridos }: { n: Nodo; props: Props; transcurridos: number }) {
  const { decenas, gasto, diasMes, abiertos, alternar } = props;
  const ids = campanasDe(n);
  const hijos = n.nivel < 3 ? n.hijos : [];
  const abierto = abiertos.has(n.clave);
  const total = [0, 1, 2].reduce((s, i) => s + sumaTramo(ids, gasto, i), 0);
  const cons = consumoMes(total, n.presDia, diasMes);
  const nombre = n.nivel === 1 ? (MARCA_BY_ID[n.nombre as keyof typeof MARCA_BY_ID]?.label ?? n.nombre) : n.nivel === 3 ? campanaCorta(n.nombre) : n.nombre;
  const fondo = n.nivel === 1 ? 'border-l-4 border-l-mc-navy bg-mc-tint2 font-bold' : n.nivel === 2 ? 'border-l-4 border-l-mc-blue bg-mc-tint font-semibold' : 'border-l-4 border-l-transparent bg-mc-sup';
  return (
    <>
      <div className={`${COLS} border-t border-mc-tint2 px-4 py-1.5 text-[13px] ${fondo} ${hijos.length ? 'cursor-pointer hover:bg-mc-tint' : ''}`} onClick={() => hijos.length && alternar(n.clave)}>
        <span className="text-mc-grey">{hijos.length ? <ChevronRight size={14} className={`transition ${abierto ? 'rotate-90' : ''}`} /> : null}</span>
        <span className={`truncate text-mc-navy ${['', '', 'pl-5', 'pl-10'][n.nivel]}`} title={n.nombre}>
          {nombre}
        </span>
        {decenas.map((d, i) => (
          <Celda key={d.n} coste={sumaTramo(ids, gasto, i)} presDia={n.presDia} d={d} />
        ))}
        <span>
          <BarraConsumo valor={cons} semaforo={semaforo(total, n.presDia, transcurridos)} marca={n.nivel === 3 ? transcurridos / diasMes : undefined} />
        </span>
      </div>
      {abierto && hijos.map((h) => <Fila key={h.clave} n={h} props={props} transcurridos={transcurridos} />)}
    </>
  );
}

export default function VistaDecenas(props: Props) {
  const { arbol, mes, diasMes, decenas, gasto } = props;
  const nombreMes = MESES[Number(mes.slice(5, 7)) - 1];
  const transcurridos = decenas.reduce((s, d) => s + d.conDatos, 0);
  const ids = arbol.flatMap(campanasDe);
  const presDia = arbol.reduce<number | null>((s, n) => (n.presDia === null ? s : (s ?? 0) + n.presDia), null);
  const totalMes = [0, 1, 2].reduce((s, i) => s + sumaTramo(ids, gasto, i), 0);
  const consMes = consumoMes(totalMes, presDia, diasMes);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {decenas.map((d, i) => {
          const g = sumaTramo(ids, gasto, i);
          const pres = presDia ? presDia * d.conDatos : null;
          const pct = pres ? g / pres : null;
          const sem = semaforo(g, presDia, d.conDatos);
          return (
            <Tarjeta key={d.n} className="px-4 py-3">
              <div className="text-[10px] font-bold uppercase tracking-[0.14em] text-mc-grey">
                {d.desde}–{d.hasta} {nombreMes}
                {d.conDatos > 0 && d.conDatos < d.dias && <span className="ml-1 normal-case tracking-normal">· {d.conDatos} de {d.dias} días</span>}
              </div>
              {d.conDatos === 0 ? (
                <div className="mt-1 text-sm text-mc-grey">Todavía no empezó</div>
              ) : (
                <>
                  <div className="mt-1 font-mono text-[18px] font-semibold text-mc-navy">{ars(g)}</div>
                  <div className="text-xs text-mc-grey">{pres === null ? 'sin presupuesto activo' : `de ${ars(pres)} presupuestados`}</div>
                  {pct !== null && (
                    <div className={`mt-1 text-xs font-semibold ${COLOR_SEMAFORO[sem].texto}`}>
                      {Math.round(pct * 100)}% · {pct > 1.05 ? `se pasó ${Math.round((pct - 1) * 100)}%` : g <= 0 ? 'sin gasto' : 'dentro del presupuesto'}
                    </div>
                  )}
                </>
              )}
            </Tarjeta>
          );
        })}
        <Tarjeta className="bg-noche-mc px-4 py-3 text-white">
          <div className="text-[10px] font-bold uppercase tracking-[0.14em] text-white/70">Mes consumido</div>
          <div className="mt-1 font-mono text-[18px] font-semibold">{consMes === null ? '—' : `${Math.round(consMes * 100)}%`}</div>
          <div className="text-xs text-white/70">
            {ars(totalMes)}
            {presDia ? ` de ${ars(presDia * diasMes)}` : ''} · día {transcurridos} de {diasMes} ({Math.round((transcurridos / diasMes) * 100)}% del mes)
          </div>
        </Tarjeta>
      </div>

      <Tarjeta className="overflow-x-auto">
        <div className="min-w-[700px]">
          <div className={`${COLS} px-4 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-mc-grey`}>
            <span />
            <span>Nivel</span>
            {decenas.map((d) => (
              <span key={d.n} className="text-right">
                {d.desde}–{d.hasta}
              </span>
            ))}
            <span>Mes consumido</span>
          </div>
          {arbol.map((n) => (
            <Fila key={n.clave} n={n} props={props} transcurridos={transcurridos} />
          ))}
        </div>
      </Tarjeta>
      <p className="text-xs text-mc-grey">
        Cada tramo compara el gasto con el presupuesto diario × los días con datos de ese tramo: verde dentro, rojo si se pasó más de 5% o no gastó. «Mes
        consumido»: gasto acumulado sobre el presupuesto del mes completo; la línea marca dónde debería estar hoy.
      </p>
    </div>
  );
}
