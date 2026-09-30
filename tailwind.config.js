/** @type {import('tailwindcss').Config} */
// Identidad MarComms (la agencia interna que presta servicios a Control Union y Peterson Solutions).
// Base del logo: azul noche #1b1e42 y azul #009ceb. Acentos de apoyo tomados de MarComms Reports (índigo para
// tarjetas destacadas, verde, dorado y rojo para estados). Nunca se usan los colores de marca de los clientes:
// Cyan #3eb2ed, Aqua #44cbce, Yellow #f1e747.
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        mc: {
          navy: '#1b1e42',
          navy2: '#1b2353',
          indigo: '#34315f',
          blue: '#009ceb',
          blue2: '#0b8fd6',
          ink: '#4f6566',
          grey: '#799495',
          tint: '#f3f6f9',
          tint2: '#e6edf3',
          hair: '#d7dee5',
          bg: '#f1f4f8',
          green: '#1fae5b',
          gold: '#c99a2e',
          red: '#d64545',
        },
      },
      fontFamily: {
        sans: ['DM Sans', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      borderRadius: { card: '12px' },
      boxShadow: {
        card: '0 1px 2px rgba(27, 30, 66, 0.05), 0 4px 14px rgba(27, 30, 66, 0.05)',
        elevada: '0 2px 4px rgba(27, 30, 66, 0.06), 0 12px 28px rgba(27, 30, 66, 0.10)',
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
        'fade-in': 'fade-in 0.3s ease-out both',
        brillo: 'brillo 1.4s linear infinite',
        barrido: 'barrido 1.3s ease-in-out infinite',
        latido: 'latido 1.6s ease-in-out infinite',
        orbita: 'orbita 1.1s linear infinite',
      },
    },
  },
  plugins: [],
};
