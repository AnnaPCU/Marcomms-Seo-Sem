/**
 * Cargas: pantalla completa con el símbolo MarComms en órbita (al abrir la app) y bloques de esqueleto con brillo
 * (dentro de cada sección mientras llegan los datos).
 */
import { useEffect, useState } from 'react';

const MENSAJES = ['Conectando con la base', 'Leyendo campañas y grupos', 'Calculando presupuestos', 'Ordenando el tablero'];

function Orbita({ tamano = 112 }: { tamano?: number }) {
  return (
    <div className="relative" style={{ width: tamano, height: tamano }}>
      {/* anillo con degradé que gira */}
      <div
        className="absolute inset-0 animate-orbita rounded-full"
        style={{
          background: 'conic-gradient(from 0deg, rgba(0,156,235,0) 0deg, #009ceb 200deg, #1fae5b 290deg, #1b1e42 360deg)',
          WebkitMask: 'radial-gradient(farthest-side, transparent calc(100% - 5px), #000 calc(100% - 4px))',
          mask: 'radial-gradient(farthest-side, transparent calc(100% - 5px), #000 calc(100% - 4px))',
        }}
      />
      <div className="absolute inset-[10px] rounded-full bg-white shadow-elevada" />
      <img src="/marca/marcomms-simbolo-160.png" alt="" className="absolute left-1/2 top-1/2 w-[46%] -translate-x-1/2 -translate-y-1/2 animate-latido" />
    </div>
  );
}

/** Pantalla completa. Se usa mientras se verifica la sesión o carga la primera vista. */
export function PantallaCarga() {
  const [i, setI] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setI((x) => (x + 1) % MENSAJES.length), 1100);
    return () => clearInterval(t);
  }, []);
  return (
    <div className="flex min-h-full flex-col items-center justify-center gap-6 bg-mc-bg">
      <Orbita />
      <div className="text-center">
        <img src="/marca/marcomms-horizontal-600.png" alt="MarComms" className="mx-auto h-6 w-auto opacity-90" />
        <p key={i} className="mt-3 animate-fade-in text-sm text-mc-grey">
          {MENSAJES[i]}…
        </p>
      </div>
      <div className="relative h-1 w-48 overflow-hidden rounded-full bg-mc-tint2">
        <div className="absolute inset-y-0 w-1/3 animate-barrido rounded-full bg-degrade-mc" />
      </div>
    </div>
  );
}

/** Carga dentro de una sección: órbita chica y texto. */
export function Cargando({ texto = 'Cargando…' }: { texto?: string }) {
  return (
    <div className="flex items-center justify-center gap-3 py-12 text-sm text-mc-grey">
      <Orbita tamano={40} />
      <span>{texto}</span>
    </div>
  );
}

/** Bloque de esqueleto con brillo que se desplaza. */
export function Esqueleto({ className = '' }: { className?: string }) {
  return (
    <div
      className={`animate-brillo rounded-card ${className}`}
      style={{ background: 'linear-gradient(90deg, #e6edf3 0%, #f3f6f9 40%, #e6edf3 80%)', backgroundSize: '800px 100%' }}
    />
  );
}

/** Esqueleto de la vista de presupuesto: fila de indicadores, barra y tabla. */
export function EsqueletoPresupuesto() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        {[0, 1, 2, 3].map((k) => (
          <Esqueleto key={k} className="h-[104px]" />
        ))}
      </div>
      <Esqueleto className="h-24" />
      <Esqueleto className="h-72" />
    </div>
  );
}

/** Esqueleto del tablero: cuatro columnas con tarjetas. */
export function EsqueletoTablero() {
  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
      {[0, 1, 2, 3].map((c) => (
        <div key={c} className="space-y-2 rounded-card bg-white/60 p-2">
          <Esqueleto className="h-10" />
          {[0, 1, 2].map((k) => (
            <Esqueleto key={k} className="h-24" />
          ))}
        </div>
      ))}
    </div>
  );
}
