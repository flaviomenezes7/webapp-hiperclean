/**
 * Barra de progresso — layout alinhado ao Figma:
 * Barra com contador "X/Y" à direita, texto abaixo.
 */
export default function ProgressBar({ enviados, total }) {
  const percentage = total > 0 ? (enviados / total) * 100 : 0;
  const allDone = total > 0 && enviados >= total;
  const remaining = total - enviados;

  return (
    <div className="progress-section">
      <div className="progress-top-row">
        <div className="progress-bar-track">
          <div
            className={`progress-bar-fill${allDone ? ' complete' : ''}`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <span className="progress-count">
          {enviados}/{total}
        </span>
      </div>
      <p className="progress-label">
        {remaining > 0
          ? `${remaining} cliente${remaining !== 1 ? 's' : ''} para contatar`
          : 'Todos contatados!'}
      </p>
    </div>
  );
}
