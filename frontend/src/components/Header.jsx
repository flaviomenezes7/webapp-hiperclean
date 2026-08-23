/**
 * Header do dashboard com data do dia, título e ícone de ação.
 */
export default function Header({ title, subtitle }) {
  const hoje = new Date();
  const dataFormatada = hoje.toLocaleDateString('pt-BR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  });

  return (
    <div className="page-header">
      <p className="page-header-date">{dataFormatada}</p>
      <div className="page-header-row">
        <h1 className="page-header-title">{title}</h1>
        <button className="page-header-action" title="Compartilhar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>
      {subtitle && <span className="page-header-subtitle">{subtitle}</span>}
    </div>
  );
}
