import { useState, useEffect, useCallback } from 'react';
import api from '../api/client';
import Modal from '../components/Modal';
import { formatTelefone } from '../utils/helpers';

const PAGE_SIZE = 20;

export default function ClientesPage({ showToast }) {
  const [clientes, setClientes] = useState([]);
  const [total, setTotal] = useState(0);
  const [busca, setBusca] = useState('');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingCliente, setEditingCliente] = useState(null);
  const [form, setForm] = useState({
    nome: '',
    telefone: '',
    data_nasc: '',
    endereco: '',
    observacoes: '',
  });

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const fetchClientes = useCallback(async () => {
    try {
      setLoading(true);
      const skip = (page - 1) * PAGE_SIZE;
      const result = await api.getClientes({ busca: busca || undefined, skip, limit: PAGE_SIZE });
      setClientes(result.items);
      setTotal(result.total);
    } catch (err) {
      showToast('Erro ao carregar clientes: ' + err.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [busca, page, showToast]);

  useEffect(() => {
    const timer = setTimeout(fetchClientes, 300);
    return () => clearTimeout(timer);
  }, [fetchClientes]);

  // Reset to page 1 when search changes
  useEffect(() => {
    setPage(1);
  }, [busca]);

  const resetForm = () => {
    setForm({ nome: '', telefone: '', data_nasc: '', endereco: '', observacoes: '' });
    setEditingCliente(null);
  };

  const openCreate = () => {
    resetForm();
    setModalOpen(true);
  };

  const openEdit = (cliente) => {
    setEditingCliente(cliente);
    setForm({
      nome: cliente.nome,
      telefone: cliente.telefone,
      data_nasc: cliente.data_nasc || '',
      endereco: cliente.endereco || '',
      observacoes: cliente.observacoes || '',
    });
    setModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      data_nasc: form.data_nasc || null,
      endereco: form.endereco || null,
      observacoes: form.observacoes || null,
    };

    try {
      if (editingCliente) {
        await api.updateCliente(editingCliente.id, payload);
        showToast('Cliente atualizado!', 'success');
      } else {
        await api.createCliente(payload);
        showToast('Cliente criado!', 'success');
      }
      setModalOpen(false);
      resetForm();
      fetchClientes();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Tem certeza que deseja remover este cliente?')) return;
    try {
      await api.deleteCliente(id);
      showToast('Cliente removido', 'success');
      fetchClientes();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  return (
    <>
      <div className="page-header">
        <div className="page-header-row">
          <h1 className="page-header-title">Clientes</h1>
          <div className="page-actions">
            <input
              className="search-input"
              type="text"
              placeholder="Buscar por nome..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
            />
            <button className="btn btn-primary" onClick={openCreate}>
              + Novo Cliente
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="loading-page"><div className="loading-spinner" /></div>
      ) : clientes.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">👥</div>
          <h2 className="empty-state-title">Nenhum cliente cadastrado</h2>
          <p className="empty-state-text">Comece adicionando seu primeiro cliente.</p>
        </div>
      ) : (
        <>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '16px' }}>
            {total} cliente{total !== 1 ? 's' : ''}
          </p>
          <table className="data-table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Telefone</th>
                <th>Nascimento</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {clientes.map((c) => (
                <tr key={c.id}>
                  <td>{c.nome}</td>
                  <td>{formatTelefone(c.telefone)}</td>
                  <td>
                    {c.data_nasc
                      ? new Date(c.data_nasc + 'T00:00:00').toLocaleDateString('pt-BR')
                      : '—'}
                  </td>
                  <td className="actions">
                    <button onClick={() => openEdit(c)} title="Editar">✏️</button>
                    <button className="delete" onClick={() => handleDelete(c.id)} title="Remover">🗑️</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="pagination-btn"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
              >
                ← Anterior
              </button>
              <span className="pagination-info">
                Página {page} de {totalPages}
              </span>
              <button
                className="pagination-btn"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
              >
                Próxima →
              </button>
            </div>
          )}
        </>
      )}

      {modalOpen && (
        <Modal
          title={editingCliente ? 'Editar Cliente' : 'Novo Cliente'}
          onClose={() => { setModalOpen(false); resetForm(); }}
          actions={
            <>
              <button className="btn btn-secondary" onClick={() => { setModalOpen(false); resetForm(); }}>
                Cancelar
              </button>
              <button className="btn btn-primary" type="submit" form="cliente-form">
                {editingCliente ? 'Salvar' : 'Criar'}
              </button>
            </>
          }
        >
          <form id="cliente-form" className="login-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="cliente-nome">Nome *</label>
              <input
                id="cliente-nome"
                className="form-input"
                value={form.nome}
                onChange={(e) => setForm({ ...form, nome: e.target.value })}
                required
                autoFocus
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="cliente-telefone">
                Telefone (55DDDNUMERO) *
              </label>
              <input
                id="cliente-telefone"
                className="form-input"
                placeholder="5511999887766"
                value={form.telefone}
                onChange={(e) => setForm({ ...form, telefone: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="cliente-nasc">Data de Nascimento</label>
              <input
                id="cliente-nasc"
                className="form-input"
                type="date"
                value={form.data_nasc}
                onChange={(e) => setForm({ ...form, data_nasc: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="cliente-endereco">Endereço</label>
              <input
                id="cliente-endereco"
                className="form-input"
                value={form.endereco}
                onChange={(e) => setForm({ ...form, endereco: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="cliente-obs">Observações</label>
              <input
                id="cliente-obs"
                className="form-input"
                value={form.observacoes}
                onChange={(e) => setForm({ ...form, observacoes: e.target.value })}
              />
            </div>
          </form>
        </Modal>
      )}
    </>
  );
}
