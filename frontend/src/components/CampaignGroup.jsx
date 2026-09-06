import { useState } from 'react';
import ClientCard from './ClientCard';

const ITEMS_PER_PAGE = 10;

/**
 * Grupo de pendentes de uma campanha — clicável com accordion.
 * Ao clicar no header, expande/recolhe a lista de contatos.
 */
export default function CampaignGroup({ grupo, onSend, sentIds }) {
  const [expanded, setExpanded] = useState(false);
  const [visibleCount, setVisibleCount] = useState(ITEMS_PER_PAGE);

  const hasMore = visibleCount < grupo.pendentes.length;
  const visibleItems = grupo.pendentes.slice(0, visibleCount);

  return (
    <div className={`campaign-group animate-fade-in-up ${expanded ? 'expanded' : ''}`}>
      <button
        className="campaign-group-header"
        onClick={() => setExpanded((v) => !v)}
        type="button"
      >
        <span className="campaign-group-emoji">{grupo.campanha_emoji || '📋'}</span>
        <span className="campaign-group-name">{grupo.campanha_nome}</span>
        <span className="campaign-group-badge">
          {grupo.total} pendente{grupo.total !== 1 ? 's' : ''}
        </span>
        <svg
          className={`campaign-group-chevron ${expanded ? 'open' : ''}`}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>
      {expanded && (
        <>
          <div className="stagger-children">
            {visibleItems.map((pendente) => (
              <ClientCard
                key={`${pendente.cliente_id}-${pendente.campanha_id}-${pendente.referencia_data}`}
                pendente={pendente}
                onSend={onSend}
                isSent={sentIds.has(
                  `${pendente.cliente_id}-${pendente.campanha_id}-${pendente.referencia_data}`
                )}
              />
            ))}
          </div>
          {hasMore && (
            <button
              className="show-more-btn"
              onClick={() => setVisibleCount((c) => c + ITEMS_PER_PAGE)}
            >
              Mostrar mais ({grupo.pendentes.length - visibleCount} restantes)
            </button>
          )}
        </>
      )}
    </div>
  );
}
