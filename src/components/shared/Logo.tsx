/**
 * Logo MarComms horizontal (o vertical) en la versión que corresponde al tema: el original sobre fondo claro y,
 * en modo oscuro, la variante con el azul noche pasado a blanco (public/marca/*-oscuro-*.png).
 */
export default function Logo({ className = '', vertical = false }: { className?: string; vertical?: boolean }) {
  const [claro, oscuro] = vertical
    ? ['/marca/marcomms-vertical-260.png', '/marca/marcomms-vertical-oscuro-260.png']
    : ['/marca/marcomms-horizontal-600.png', '/marca/marcomms-horizontal-oscuro-600.png'];
  return (
    <>
      <img src={claro} alt="MarComms" className={`${className} dark:hidden`} />
      <img src={oscuro} alt="MarComms" className={`${className} hidden dark:block`} />
    </>
  );
}
