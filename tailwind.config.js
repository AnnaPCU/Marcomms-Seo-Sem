/** @type {import('tailwindcss').Config} */
// Identidad MarComms (la agencia interna que presta servicios a Control Union y Peterson Solutions).
// Tokens sacados del logo: azul marino #1b1e42 y azul #009ceb. Los contenidos de cada marca cliente
// se muestran en secciones separadas y nunca con los colores de la otra marca.
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        mc: {
          navy: '#1b1e42',
          navy2: '#1b2353',
          blue: '#009ceb',
          blue2: '#0b8fd6',
          ink: '#4f6566',
          grey: '#799495',
          tint: '#f3f6f9',
          tint2: '#e6edf3',
          hair: '#d7dee5',
          bg: '#f7f9fb',
        },
      },
      fontFamily: {
        sans: ['DM Sans', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      borderRadius: { card: '12px' },
      boxShadow: { card: '0 1px 2px rgba(27, 30, 66, 0.06), 0 6px 18px rgba(27, 30, 66, 0.06)' },
      keyframes: {
        'fade-in': { '0%': { opacity: '0', transform: 'translateY(6px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
      },
      animation: { 'fade-in': 'fade-in 0.25s ease-out' },
    },
  },
  plugins: [],
};
