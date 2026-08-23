import { useState } from 'react';

/**
 * Card de um cliente pendente — design flat sem background,
 * avatar monocromático, botão "Enviar" com ícone SVG.
 */
export default function ClientCard({ pendente, onSend, isSent }) {
  const [sending, setSending] = useState(false);

  const handleSend = async () => {
    if (isSent || sending) return;
    setSending(true);

    // 1. Open WhatsApp in new tab
    window.open(pendente.link_whatsapp, '_blank', 'noopener,noreferrer');

    // 2. Mark as sent in backend
    try {
      await onSend({
        cliente_id: pendente.cliente_id,
        campanha_id: pendente.campanha_id,
        referencia_data: pendente.referencia_data,
      });
    } catch (err) {
      console.error('Erro ao registrar envio:', err);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className={`client-card ${isSent ? 'sent' : ''}`}>
      <div className="client-avatar">
        {pendente.cliente_iniciais}
      </div>
      <div className="client-info">
        <div className="client-name">{pendente.cliente_nome}</div>
        <div className="client-message-preview">
          {pendente.mensagem_formatada}
        </div>
      </div>
      <button
        className={`client-card-send-btn ${isSent ? 'sent' : ''}`}
        onClick={handleSend}
        disabled={isSent || sending}
        title={isSent ? 'Mensagem enviada' : 'Abrir WhatsApp e enviar'}
      >
        {isSent ? (
          '✓ Enviado'
        ) : sending ? (
          '...'
        ) : (
          <>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
            Enviar
          </>
        )}
      </button>
    </div>
  );
}
