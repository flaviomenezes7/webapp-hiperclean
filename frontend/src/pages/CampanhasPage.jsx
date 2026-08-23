import { useState, useEffect, useCallback } from 'react';
import api from '../api/client';
import Modal from '../components/Modal';
import { TIPO_GATILHO_LABELS } from '../utils/helpers';

export default function CampanhasPage({ showToast }) {
  const [campanhas, setCampanhas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingCampanha, setEditingCampanha] = useState(null);
  const [form, setForm] = useState({
    nome: '',
    emoji: '',
    tipo_gatilho: 'DIAS_APOS_ATENDIMENTO',
    dias_offset: '180',
    mes_fixo: '',
    dia_fixo: '',
    template_msg: '',
    ativa: true,
  });

  const fetchCampanhas = useCallback(async () => {
    try {
      setLoading(true);
      const result = await api.getCampanhas();
      setCampanhas(result);
    } catch (err) {
      showToast('Erro ao carregar campanhas: ' + err.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    fetchCampanhas();
  }, [fetchCampanhas]);

  const resetForm = () => {
    setForm({
      nome: '',
      emoji: '',
      tipo_gatilho: 'DIAS_APOS_ATENDIMENTO',
      dias_offset: '180',
      mes_fixo: '',
      dia_fixo: '',
      template_msg: '',
      ativa: true,
    });
    setEditingCampanha(null);
  };

  const openCreate = () => {
    resetForm();
    setModalOpen(true);
  };

  const openEdit = (c) => {
    setEditingCampanha(c);
    setForm({
      nome: c.nome,
      emoji: c.emoji || '',
      tipo_gatilho: c.tipo_gatilho,
      dias_offset: c.dias_offset != null ? String(c.dias_offset) : '',
      mes_fixo: c.mes_fixo != null ? String(c.mes_fixo) : '',
      dia_fixo: c.dia_fixo != null ? String(c.dia_fixo) : '',
      template_msg: c.template_msg,
      ativa: c.ativa,
    });
    setModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      nome: form.nome,
      emoji: form.emoji || null,
      tipo_gatilho: form.tipo_gatilho,
      dias_offset: form.dias_offset ? parseInt(form.dias_offset) : null,
      mes_fixo: form.mes_fixo ? parseInt(form.mes_fixo) : null,
      dia_fixo: form.dia_fixo ? parseInt(form.dia_fixo) : null,
      template_msg: form.template_msg,
      ativa: form.ativa,
    };

    try {
      if (editingCampanha) {
        await api.updateCampanha(editingCampanha.id, payload);
        showToast('Campanha atualizada!', 'success');
      } else {
        await api.createCampanha(payload);
        showToast('Campanha criada!', 'success');
      }
      setModalOpen(false);
      resetForm();
      fetchCampanhas();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  const handleToggle = async (id) => {
    try {
      await api.toggleCampanha(id);
      fetchCampanhas();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Remover esta campanha?')) return;
    try {
      await api.deleteCampanha(id);
      showToast('Campanha removida', 'success');
      fetchCampanhas();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  const placeholderHint = () => {
    if (form.tipo_gatilho === 'ANIVERSARIO') {
      return 'Ex: Feliz aniversário, {nome}! 🎂 Que seu dia seja incrível!';
    }
    if (form.tipo_gatilho === 'DIAS_APOS_ATENDIMENTO') {
      return 'Ex: Olá, {nome}! Já faz {dias} dias que limpamos seu {servico}. Que tal agendar uma nova limpeza?';
    }
    return 'Ex: Olá, {nome}! A Hiper Clean deseja um ótimo dia para você!';
  };

  return (
    <>
      <div className="page-header">
        <div className="page-header-row">
          <h1 className="page-header-title">Campanhas</h1>
          <div className="page-actions">
            <button className="btn btn-primary" onClick={openCreate}>
              + Nova Campanha
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="loading-page"><div className="loading-spinner" /></div>
      ) : campanhas.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📣</div>
          <h2 className="empty-state-title">Nenhuma campanha configurada</h2>
          <p className="empty-state-text">
            Crie sua primeira campanha para começar a gerar lembretes automáticos.
          </p>
        </div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th></th>
              <th>Nome</th>
              <th>Tipo</th>
              <th>Detalhes</th>
              <th>Ativa</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {campanhas.map((c) => (
              <tr key={c.id} style={{ opacity: c.ativa ? 1 : 0.5 }}>
                <td style={{ fontSize: '1.2rem', width: '30px' }}>{c.emoji || '📋'}</td>
                <td>{c.nome}</td>
                <td>{TIPO_GATILHO_LABELS[c.tipo_gatilho] || c.tipo_gatilho}</td>
                <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {c.tipo_gatilho === 'DIAS_APOS_ATENDIMENTO' && `${c.dias_offset} dias`}
                  {c.tipo_gatilho === 'DATA_FIXA' && `${String(c.dia_fixo).padStart(2, '0')}/${String(c.mes_fixo).padStart(2, '0')}`}
                  {c.tipo_gatilho === 'ANIVERSARIO' && 'Automático'}
                </td>
                <td>
                  <button
                    className={`toggle-switch ${c.ativa ? 'active' : ''}`}
                    onClick={() => handleToggle(c.id)}
                    title={c.ativa ? 'Desativar' : 'Ativar'}
                  />
                </td>
                <td className="actions">
                  <button onClick={() => openEdit(c)} title="Editar">✏️</button>
                  <button className="delete" onClick={() => handleDelete(c.id)} title="Remover">🗑️</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {modalOpen && (
        <Modal
          title={editingCampanha ? 'Editar Campanha' : 'Nova Campanha'}
          onClose={() => { setModalOpen(false); resetForm(); }}
          actions={
            <>
              <button className="btn btn-secondary" onClick={() => { setModalOpen(false); resetForm(); }}>
                Cancelar
              </button>
              <button className="btn btn-primary" type="submit" form="campanha-form">
                {editingCampanha ? 'Salvar' : 'Criar'}
              </button>
            </>
          }
        >
          <form id="campanha-form" className="login-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="camp-nome">Nome *</label>
              <input
                id="camp-nome"
                className="form-input"
                placeholder="Ex: Lembrete de limpeza"
                value={form.nome}
                onChange={(e) => setForm({ ...form, nome: e.target.value })}
                required
                autoFocus
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="camp-emoji">Emoji</label>
              <input
                id="camp-emoji"
                className="form-input"
                placeholder="🎂 ou 🕐"
                value={form.emoji}
                onChange={(e) => setForm({ ...form, emoji: e.target.value })}
                maxLength={4}
                style={{ width: '80px' }}
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="camp-tipo">Tipo de Gatilho *</label>
              <select
                id="camp-tipo"
                className="form-select"
                value={form.tipo_gatilho}
                onChange={(e) => setForm({ ...form, tipo_gatilho: e.target.value })}
                required
              >
                {Object.entries(TIPO_GATILHO_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>

            {form.tipo_gatilho === 'DIAS_APOS_ATENDIMENTO' && (
              <div className="form-group">
                <label className="form-label" htmlFor="camp-dias">Dias após atendimento *</label>
                <input
                  id="camp-dias"
                  className="form-input"
                  type="number"
                  min="1"
                  placeholder="180"
                  value={form.dias_offset}
                  onChange={(e) => setForm({ ...form, dias_offset: e.target.value })}
                  required
                />
              </div>
            )}

            {form.tipo_gatilho === 'DATA_FIXA' && (
              <div style={{ display: 'flex', gap: '12px' }}>
                <div className="form-group" style={{ flex: 1 }}>
                  <label className="form-label" htmlFor="camp-dia">Dia *</label>
                  <input
                    id="camp-dia"
                    className="form-input"
                    type="number"
                    min="1"
                    max="31"
                    placeholder="25"
                    value={form.dia_fixo}
                    onChange={(e) => setForm({ ...form, dia_fixo: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group" style={{ flex: 1 }}>
                  <label className="form-label" htmlFor="camp-mes">Mês *</label>
                  <input
                    id="camp-mes"
                    className="form-input"
                    type="number"
                    min="1"
                    max="12"
                    placeholder="12"
                    value={form.mes_fixo}
                    onChange={(e) => setForm({ ...form, mes_fixo: e.target.value })}
                    required
                  />
                </div>
              </div>
            )}

            <div className="form-group">
              <label className="form-label" htmlFor="camp-template">
                Template da Mensagem *
              </label>
              <textarea
                id="camp-template"
                className="form-input"
                style={{ minHeight: '100px', resize: 'vertical' }}
                placeholder={placeholderHint()}
                value={form.template_msg}
                onChange={(e) => setForm({ ...form, template_msg: e.target.value })}
                required
              />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Placeholders: {'{'} nome {'}'}, {'{'} dias {'}'}, {'{'} servico {'}'}
              </span>
            </div>
          </form>
        </Modal>
      )}
    </>
  );
}
