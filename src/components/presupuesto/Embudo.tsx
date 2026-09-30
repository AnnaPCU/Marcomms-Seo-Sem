/** Embudo impresión → clic → conversión, con el degradé azul noche → azul → verde de MarComms Reports. */
import { ars, entero } from '@/utils/formato';

interface Props {
  impresiones: number;
  clics: number;
  conv: number;
  coste: number;
}

function Escalon({ ancho, color, etiqueta, valor, nota }: { ancho: number; color: string; etiqueta: string; valor: string; nota: string }) {
  const lado = (100 - ancho) / 2;
  return (
    <div className="relative mx-auto h-[74px]" style={{ width: '100%' }}>
      <div
        className="absolute inset-0 grid place-items-center text-center text-white"
        style={{ background: color, clipPath: `polygon(${lado}% 0, ${100 - lado}% 0, ${100 - lado - 6}% 100%, ${lado + 6}% 100%)` }}
      >
        <div>
          <div className="text-[10px] font-bold uppercase tracking-[0.14em] text-white/80">{etiqueta}</div>
          <div className="font-mono text-xl font-semibold leading-tight">{valor}</div>
          <div className="text-[11px] text-white/80">{nota}</div>
        </div>
      </div>
    </div>
  );
}

function Paso({ texto, valor }: { texto: string; valor: string }) {
  return (
    <div className="my-1 flex items-center justify-center gap-2 text-[11px] text-mc-grey">
      <span className="h-px w-10 bg-mc-hair" />
      {texto} <b className="font-mono text-mc-blue2">{valor}</b>
      <span className="h-px w-10 bg-mc-hair" />
    </div>
  );
}

function Dato({ color, etiqueta, valor, nota }: { color: string; etiqueta: string; valor: string; nota: string }) {
  return (
    <div className="rounded-lg bg-mc-tint px-4 py-3">
      <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.14em] text-mc-grey">
        <span className={`h-2.5 w-2.5 rounded-sm ${color}`} />
        {etiqueta}
      </div>
      <div className="mt-1 font-mono text-lg font-semibold text-mc-navy">{valor}</div>
      <div className="text-[11px] text-mc-grey">{nota}</div>
    </div>
  );
}

export default function Embudo({ impresiones, clics, conv, coste }: Props) {
  const ctr = impresiones ? clics / impresiones : 0;
  const tasa = clics ? conv / clics : 0;
  const pct = (x: number) => `${(x * 100).toFixed(2).replace('.', ',')}%`;
  return (
    <div className="grid grid-cols-1 items-center gap-6 lg:grid-cols-[1.4fr_1fr]">
      <div>
        <Escalon ancho={100} color="linear-gradient(135deg, #1b1e42, #34315f)" etiqueta="Impresiones" valor={entero(impresiones)} nota="veces que se mostraron los anuncios" />
        <Paso texto="CTR · impresión → clic" valor={pct(ctr)} />
        <Escalon ancho={78} color="linear-gradient(135deg, #0b8fd6, #009ceb)" etiqueta="Clics" valor={entero(clics)} nota={`CPC ${ars(clics ? coste / clics : 0)}`} />
        <Paso texto="Conversión · clic → lead" valor={pct(tasa)} />
        <Escalon ancho={56} color="linear-gradient(135deg, #17964d, #1fae5b)" etiqueta="Conversiones" valor={entero(conv)} nota={conv ? `${ars(coste / conv)} cada una` : 'sin conversiones en el período'} />
      </div>
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-1">
        <Dato color="bg-mc-navy" etiqueta="Coste total" valor={ars(coste)} nota="Inversión ejecutada en el período" />
        <Dato color="bg-mc-blue" etiqueta="CPC medio" valor={ars(clics ? coste / clics : 0)} nota="Coste promedio por clic" />
        <Dato color="bg-mc-green" etiqueta="Coste por conversión" valor={conv ? ars(coste / conv) : '—'} nota={conv ? `${entero(conv)} conversiones` : 'Sin conversiones'} />
      </div>
    </div>
  );
}
