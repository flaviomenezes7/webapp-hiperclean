/**
 * Ícones SVG inline para o app — substitui emojis por ícones consistentes.
 * Todos os ícones recebem as props padrão de SVG (className, style, etc.)
 */

const defaultProps = {
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.8,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
  width: 18,
  height: 18,
};

function Icon({ children, ...props }) {
  return <svg {...defaultProps} {...props}>{children}</svg>;
}

/** Aniversário / Presente */
export function IconCake(props) {
  return (
    <Icon {...props}>
      <path d="M20 21v-8a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8" />
      <path d="M4 16s.5-1 2-1 2.5 2 4 2 2.5-2 4-2 2.5 2 4 2 2-1 2-1" />
      <path d="M2 21h20" />
      <path d="M7 8v3" />
      <path d="M12 8v3" />
      <path d="M17 8v3" />
      <path d="M7 4h.01" />
      <path d="M12 4h.01" />
      <path d="M17 4h.01" />
    </Icon>
  );
}

/** Relógio / Lembrete */
export function IconClock(props) {
  return (
    <Icon {...props}>
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </Icon>
  );
}

/** Natal / Árvore */
export function IconTree(props) {
  return (
    <Icon {...props}>
      <path d="M12 3l-7 9h4l-3 9h12l-3-9h4z" />
      <line x1="12" y1="21" x2="12" y2="24" />
    </Icon>
  );
}

/** Estrela / Destaque */
export function IconStar(props) {
  return (
    <Icon {...props}>
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
    </Icon>
  );
}

/** Megafone / Campanha */
export function IconMegaphone(props) {
  return (
    <Icon {...props}>
      <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
      <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
      <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
    </Icon>
  );
}

/** Clipboard / Genérico */
export function IconClipboard(props) {
  return (
    <Icon {...props}>
      <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
      <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
    </Icon>
  );
}

/** Check / Concluído */
export function IconCheck(props) {
  return (
    <Icon {...props}>
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </Icon>
  );
}

/** Lápis / Editar */
export function IconEdit(props) {
  return (
    <Icon {...props} width={16} height={16}>
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
    </Icon>
  );
}

/** Lixeira / Deletar */
export function IconTrash(props) {
  return (
    <Icon {...props} width={16} height={16}>
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    </Icon>
  );
}

/** Usuários */
export function IconUsers(props) {
  return (
    <Icon {...props}>
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </Icon>
  );
}

/**
 * Mapeia um tipo de gatilho ou nome de campanha para o ícone correto.
 * Usado pelo CampaignGroup para renderizar o ícone no lugar do emoji.
 */
export function getCampaignIcon(tipoGatilho, campanhaNome) {
  // Por tipo de gatilho
  if (tipoGatilho === 'ANIVERSARIO') return IconCake;
  if (tipoGatilho === 'DIAS_APOS_ATENDIMENTO') return IconClock;
  if (tipoGatilho === 'DATA_FIXA') {
    // Verificar se é natal pelo nome
    const nomeLower = (campanhaNome || '').toLowerCase();
    if (nomeLower.includes('natal')) return IconTree;
    if (nomeLower.includes('star') || nomeLower.includes('destaque')) return IconStar;
    return IconClipboard;
  }
  return IconClipboard;
}
