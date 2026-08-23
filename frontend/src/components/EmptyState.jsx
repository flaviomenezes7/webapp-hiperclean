/**
 * Estado vazio — mostrado quando não há pendentes para o dia.
 */
export default function EmptyState() {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">🎉</div>
      <h2 className="empty-state-title">Tudo em dia!</h2>
      <p className="empty-state-text">
        Nenhum cliente para contatar hoje. Aproveite para cadastrar novos
        clientes ou verificar suas campanhas.
      </p>
    </div>
  );
}
