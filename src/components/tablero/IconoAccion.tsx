/** Ícono de cada tipo de mejora (ver ACCIONES en constants/estados). */
import { Ban, CircleHelp, FileText, KeyRound, Megaphone, Network, PauseCircle, type LucideIcon } from 'lucide-react';

const ICONOS: Record<string, LucideIcon> = {
  anuncio: Megaphone,
  keywords: KeyRound,
  negativas: Ban,
  estructura: Network,
  pausa: PauseCircle,
  landing: FileText,
  revisar: CircleHelp,
};

export default function IconoAccion({ id, size = 12, className }: { id: string; size?: number; className?: string }) {
  const Icono = ICONOS[id] ?? CircleHelp;
  return <Icono size={size} className={className} aria-hidden />;
}
