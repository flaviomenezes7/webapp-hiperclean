import { useState, useEffect, useCallback } from 'react';
import api from '../api/client';
import Modal from '../components/Modal';
import { TIPO_SERVICO_LABELS } from '../utils/helpers';

const PAGE_SIZE = 20;

export default function AtendimentosPage({ showToast }) {
  const [atendimentos, setAtendimentos] = useState([]);
  const [total, setTotal] = useState(0);
  const [clientes, setClientes] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingAtend, setEditingAtend] = useState(null);
  const [form, setForm] = useState({
    cliente_id: '',
    tipo_servico: 'SOFA',
    data_atend: new Date().toISOString().split('T')[0],
    observacoes: '',
    valor: '',
  });

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const skip = (page - 1) * PAGE_SIZE;
      const [atendResult, clientesResult] = await Promise.all([
        api.getAtendimentos({ skip, limit: PAGE_SIZE }),
        api.getClientes({ limit: 500 }),
      ]);
      setAtendimentos(atendResult.items);
      setTotal(atendResult.total);
      setClientes(clientesResult.items);
    } catch (err) {
      showToast('Erro ao carregar dados: ' + err.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [page, showToast]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const resetForm = () => {
    setForm({
      cliente_id: '',
      tipo_servico: 'SOFA',
      data_atend: new Date().toISOString().split('T')[0],
      observacoes: '',
      valor: '',
    });
    setEditingAtend(null);
  };

  const openCreate = () => {
    resetForm();
    setModalOpen(true);
  };

  const openEdit = (atend) => {
    setEditingAtend(atend);
    setForm({
      cliente_id: atend.cliente_id,
      tipo_servico: atend.tipo_servico,
      data_atend: atend.data_atend,
      observacoes: atend.observacoes || '',
      valor: atend.valor != null ? String(atend.valor) : '',
    });
    setModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      valor: form.valor ? parseFloat(form.valor) : null,
      observacoes: form.observacoes || null,
    };

    try {
      if (editingAtend) {
        const { cliente_id, ...updatePayload } = payload;
        await api.updateAtendimento(editingAtend.id, updatePayload);
        showToast('Atendimento atualizado!', 'success');
      } else {
        await api.createAtendimento(payload);
        showToast('Atendimento registrado!', 'success');
      }
      setModalOpen(false);
      resetForm();
      fetchData();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Remover este atendimento?')) return;
    try {
      await api.deleteAtendimento(id);
      showToast('Atendimento removido', 'success');
      fetchData();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  return (
    <>
      <div className="page-header">
        <div className="page-header-row">
          <h1 className="page-header-title">Atendimentos</h1>
          <div className="page-actions">
            <button className="btn btn-primary" onClick={openCreate}>
              + Novo Atendimento
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="loading-page"><div className="loading-spinner" /></div>
      ) : atendimentos.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📋</div>
          <h2 className="empty-state-title">Nenhum atendimento registrado</h2>
          <p className="empty-state-text">Registre o primeiro atendimento de um cliente.</p>
        </div>
      ) : (
        <>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '16px' }}>
            {total} atendimento{total !== 1 ? 's' : ''}
          </p>
          <table className="data-table">
            <thead>
              <tr>
                <th>Cliente</th>
                <th>Serviço</th>
                <th>Data</th>
                <th>Valor</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {atendimentos.map((a) => (
                <tr key={a.id}>
                  <td>{a.cliente_nome || '—'}</td>
                  <td>{TIPO_SERVICO_LABELS[a.tipo_servico] || a.tipo_servico}</td>
                  <td>{new Date(a.data_atend + 'T00:00:00').toLocaleDateString('pt-BR')}</td>
                  <td>{a.valor != null ? `R$ ${parseFloat(a.valor).toFixed(2)}` : '—'}</td>
                  <td className="actions">
                    <button onClick={() => openEdit(a)} title="Editar">✏️</button>
                    <button className="delete" onClick={() => handleDelete(a.id)} title="Remover">🗑️</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

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
          title={editingAtend ? 'Editar Atendimento' : 'Novo Atendimento'}
          onClose={() => { setModalOpen(false); resetForm(); }}
          actions={
            <>
              <button className="btn btn-secondary" onClick={() => { setModalOpen(false); resetForm(); }}>
                Cancelar
              </button>
              <button className="btn btn-primary" type="submit" form="atend-form">
                {editingAtend ? 'Salvar' : 'Registrar'}
              </button>
            </>
          }
        >
          <form id="atend-form" className="login-form" onSubmit={handleSubmit}>
            {!editingAtend && (
              <div className="form-group">
                <label className="form-label" htmlFor="atend-cliente">Cliente *</label>
                <select
                  id="atend-cliente"
                  className="form-select"
                  value={form.cliente_id}
                  onChange={(e) => setForm({ ...form, cliente_id: e.target.value })}
                  required
                >
                  <option value="">Selecione o cliente</option>
                  {clientes.map((c) => (
                    <option key={c.id} value={c.id}>{c.nome}</option>
                  ))}
                </select>
              </div>
            )}
            <div className="form-group">
              <label className="form-label" htmlFor="atend-servico">Tipo de Serviço *</label>
              <select
                id="atend-servico"
                className="form-select"
                value={form.tipo_servico}
                onChange={(e) => setForm({ ...form, tipo_servico: e.target.value })}
                required
              >
                {Object.entries(TIPO_SERVICO_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="atend-data">Data do Atendimento *</label>
              <input
                id="atend-data"
                className="form-input"
                type="date"
                value={form.data_atend}
                onChange={(e) => setForm({ ...form, data_atend: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="atend-valor">Valor (R$)</label>
              <input
                id="atend-valor"
                className="form-input"
                type="number"
                step="0.01"
                min="0"
                placeholder="150.00"
                value={form.valor}
                onChange={(e) => setForm({ ...form, valor: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="atend-obs">Observações</label>
              <input
                id="atend-obs"
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
