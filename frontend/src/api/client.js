const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Wrapper around fetch that handles auth headers and JSON parsing.
 */
async function request(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  // Handle 401 — redirect to login
  if (res.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
    throw new Error('Sessão expirada');
  }

  // Handle no-content responses
  if (res.status === 204) {
    return null;
  }

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || `Erro ${res.status}`);
  }

  return data;
}

const api = {
  // Auth
  login: (email, password) => {
    const body = new URLSearchParams();
    body.append('username', email);
    body.append('password', password);
    return fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body,
    }).then(async (res) => {
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Login falhou');
      return data;
    });
  },

  // Pendentes
  getPendentesHoje: (data) => {
    const params = data ? `?data=${data}` : '';
    return request(`/pendentes/hoje${params}`);
  },

  // Envios
  registrarEnvio: (payload) =>
    request('/envios', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Clientes
  getClientes: (params = {}) => {
    const searchParams = new URLSearchParams();
    if (params.busca) searchParams.set('busca', params.busca);
    if (params.skip != null) searchParams.set('skip', params.skip);
    if (params.limit != null) searchParams.set('limit', params.limit);
    const qs = searchParams.toString();
    return request(`/clientes${qs ? '?' + qs : ''}`);
  },
  importExcel: (file) => {
    const token = localStorage.getItem('token');
    const formData = new FormData();
    formData.append('file', file);
    return fetch(`${API_BASE}/clientes/importar-excel`, {
      method: 'POST',
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: formData,
    }).then(async (res) => {
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Erro na importação');
      return data;
    });
  },
  createCliente: (data) =>
    request('/clientes', { method: 'POST', body: JSON.stringify(data) }),
  updateCliente: (id, data) =>
    request(`/clientes/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteCliente: (id) =>
    request(`/clientes/${id}`, { method: 'DELETE' }),

  // Atendimentos
  getAtendimentos: (params = {}) => {
    const searchParams = new URLSearchParams();
    if (params.cliente_id) searchParams.set('cliente_id', params.cliente_id);
    if (params.skip != null) searchParams.set('skip', params.skip);
    if (params.limit != null) searchParams.set('limit', params.limit);
    const qs = searchParams.toString();
    return request(`/atendimentos${qs ? '?' + qs : ''}`);
  },
  createAtendimento: (data) =>
    request('/atendimentos', { method: 'POST', body: JSON.stringify(data) }),
  updateAtendimento: (id, data) =>
    request(`/atendimentos/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteAtendimento: (id) =>
    request(`/atendimentos/${id}`, { method: 'DELETE' }),

  // Campanhas
  getCampanhas: () => request('/campanhas'),
  createCampanha: (data) =>
    request('/campanhas', { method: 'POST', body: JSON.stringify(data) }),
  updateCampanha: (id, data) =>
    request(`/campanhas/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteCampanha: (id) =>
    request(`/campanhas/${id}`, { method: 'DELETE' }),
  toggleCampanha: (id) =>
    request(`/campanhas/${id}/toggle`, { method: 'PATCH' }),
};

export default api;
