import { useState, useCallback } from 'react';

/**
 * Simple toast notification hook.
 * Returns [toast, showToast] — render the Toast component in your layout.
 */
export function useToast(duration = 3000) {
  const [toast, setToast] = useState(null);

  const showToast = useCallback((message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), duration);
  }, [duration]);

  return [toast, showToast];
}
