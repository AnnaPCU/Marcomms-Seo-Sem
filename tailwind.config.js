/** @type {import('tailwindcss').Config} */
const v = (nombre) => `rgb(var(${nombre}) / <alpha-value>)`;
const escala = (color, tonos) => Object.fromEntries(tonos.map((t) => [t, v(`--${color}-${t}`)]));

// Identidad MarComms (la agencia interna que presta servicios a Control Union y Peterson Solutions).
// Base del logo: azul noche #1b1e42 y azul #009ceb. Acentos de apoyo tomados de MarComms Reports (índigo para
// tarjetas destacadas, verde, dorado y rojo para estados). Nunca se usan los colores de marca de los clientes:
// Cyan #3eb2ed, Aqua #44cbce, Yellow #f1e747.
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      // Los colores son variables CSS (index.css): cambian solos entre el tema claro y el oscuro (clase .dark en <html>).
      colors: {
        mc: {
          navy: v('--mc-navy'), // texto fuerte y títulos
          fuerte: v('--mc-fuerte'), // relleno oscuro (botones activos, chips): azul noche en claro, índigo en oscuro
          navy2: v('--mc-navy2'),
          indigo: v('--mc-indigo'),
          blue: v('--mc-blue'),
          blue2: v('--mc-blue2'),
          ink: v('--mc-ink'),
          grey: v('--mc-grey'),
          tint: v('--mc-tint'),
          tint2: v('--mc-tint2'),
          hair: v('--mc-hair'),
          bg: v('--mc-bg'),
          sup: v('--mc-sup'), // superficie de tarjetas y paneles: blanco en claro
          green: v('--mc-green'),
          gold: v('--mc-gold'),
          red: v('--mc-red'),
        },
        // tonos de estado de Tailwind que se usan en chips y avisos: en oscuro, fondos apagados y textos claros
        red: escala('red', [50, 100, 200, 300, 700, 800]),
        emerald: escala('emerald', [50, 100, 200, 700, 800]),
        amber: escala('amber', [50, 100, 200, 800]),
        sky: escala('sky', [50, 100, 200]),
      },
      fontFamily: {
        sans: ['DM Sans', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      borderRadius: { card: '12px' },
      boxShadow: {
        card: '0 1px 2px rgb(var(--sombra) / 0.05), 0 4px 14px rgb(var(--sombra) / 0.05)',
        elevada: '0 2px 4px rgb(var(--sombra) / 0.06), 0 12px 28px rgb(var(--sombra) / 0.10)',
      },
      backgroundImage: {
        'degrade-mc': 'linear-gradient(90deg, #1b1e42 0%, #009ceb 55%, #1fae5b 100%)',
        'noche-mc': 'linear-gradient(135deg, #1b1e42 0%, #34315f 100%)',
      },
      keyframes: {
        'fade-in': { '0%': { opacity: '0', transform: 'translateY(6px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
        brillo: { '0%': { backgroundPosition: '-400px 0' }, '100%': { backgroundPosition: '400px 0' } },
        barrido: { '0%': { transform: 'translateX(-100%)' }, '100%': { transform: 'translateX(250%)' } },
        latido: { '0%, 100%': { transform: 'scale(1)', opacity: '1' }, '50%': { transform: 'scale(0.92)', opacity: '0.85' } },
        orbita: { '0%': { transform: 'rotate(0deg)' }, '100%': { transform: 'rotate(360deg)' } },
      },
      animation: {
        // backwards y no both: al terminar no queda transform aplicado (un transform en un ancestro rompe position: fixed)
        'fade-in': 'fade-in 0.3s ease-out backwards',
        brillo: 'brillo 1.4s linear infinite',
        barrido: 'barrido 1.3s ease-in-out infinite',
        latido: 'latido 1.6s ease-in-out infinite',
        orbita: 'orbita 1.1s linear infinite',
      },
    },
  },
  plugins: [],
};
