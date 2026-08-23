import { useState } from 'react';
import ClientCard from './ClientCard';

const ITEMS_PER_PAGE = 10;

/**
 * Grupo de pendentes de uma campanha — com paginação interna "Mostrar mais".
 */
export default function CampaignGroup({ grupo, onSend, sentIds }) {
  const [visibleCount, setVisibleCount] = useState(ITEMS_PER_PAGE);

  const hasMore = visibleCount < grupo.pendentes.length;
  const visibleItems = grupo.pendentes.slice(0, visibleCount);

  return (
    <div className="campaign-group animate-fade-in-up">
      <div className="campaign-group-header">
        <span className="campaign-group-emoji">{grupo.campanha_emoji || '📋'}</span>
        <span className="campaign-group-name">{grupo.campanha_nome}</span>
        <span className="campaign-group-badge">
          {grupo.total} pendente{grupo.total !== 1 ? 's' : ''}
        </span>
      </div>
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
    </div>
  );
}
