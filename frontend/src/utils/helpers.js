/**
 * Monta um link wa.me com texto pré-preenchido.
 * O telefone já deve estar no formato 55DDDNUMERO (somente dígitos).
 */
export function buildWhatsappLink(telefone, mensagem) {
  const encoded = encodeURIComponent(mensagem);
  return `https://wa.me/${telefone}?text=${encoded}`;
}

/**
 * Abre o WhatsApp em uma nova aba com a mensagem pré-preenchida.
 */
export function openWhatsapp(telefone, mensagem) {
  const link = buildWhatsappLink(telefone, mensagem);
  window.open(link, '_blank', 'noopener,noreferrer');
}

/**
 * Formata telefone para exibição: 55 11 99988-7766
 */
export function formatTelefone(telefone) {
  if (!telefone) return '';
  const digits = telefone.replace(/\D/g, '');
  if (digits.length === 13) {
    return `+${digits.slice(0, 2)} ${digits.slice(2, 4)} ${digits.slice(4, 9)}-${digits.slice(9)}`;
  }
  if (digits.length === 12) {
    return `+${digits.slice(0, 2)} ${digits.slice(2, 4)} ${digits.slice(4, 8)}-${digits.slice(8)}`;
  }
  return telefone;
}

/**
 * Maps for human-readable labels.
 */
export const TIPO_SERVICO_LABELS = {
  SOFA: 'Sofá',
  COLCHAO: 'Colchão',
  CADEIRA: 'Cadeira',
  TAPETE: 'Tapete',
  CORTINA: 'Cortina',
  POLTRONA: 'Poltrona',
  BANCO_AUTOMOTIVO: 'Banco Automotivo',
  OUTRO: 'Outro',
};

export const TIPO_GATILHO_LABELS = {
  ANIVERSARIO: 'Aniversário',
  DIAS_APOS_ATENDIMENTO: 'Dias após atendimento',
  DATA_FIXA: 'Data fixa',
};
