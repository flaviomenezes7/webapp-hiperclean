/**
 * Componente de Toast notification.
 */
export default function Toast({ toast }) {
  if (!toast) return null;

  return (
    <div className={`toast ${toast.type}`} role="alert">
      {toast.type === 'success' && '✓ '}
      {toast.type === 'error' && '✕ '}
      {toast.message}
    </div>
  );
}
