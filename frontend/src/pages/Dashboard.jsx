import { useState, useEffect, useCallback, useMemo } from 'react';
import api from '../api/client';
import Header from '../components/Header';
import ProgressBar from '../components/ProgressBar';
import CampaignGroup from '../components/CampaignGroup';
import EmptyState from '../components/EmptyState';

export default function Dashboard({ showToast }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sentIds, setSentIds] = useState(new Set());
  const [busca, setBusca] = useState('');

  const fetchPendentes = useCallback(async () => {
    try {
      setLoading(true);
      const result = await api.getPendentesHoje();
      setData(result);
    } catch (err) {
      showToast('Erro ao carregar pendentes: ' + err.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    fetchPendentes();
  }, [fetchPendentes]);

  const handleSend = async (payload) => {
    try {
      await api.registrarEnvio(payload);
      const key = `${payload.cliente_id}-${payload.campanha_id}-${payload.referencia_data}`;
      setSentIds((prev) => new Set(prev).add(key));
      showToast('Mensagem registrada como enviada!', 'success');
    } catch (err) {
      // 409 = already sent, not an error for the user
      if (err.message.includes('409') || err.message.includes('já registrado')) {
        const key = `${payload.cliente_id}-${payload.campanha_id}-${payload.referencia_data}`;
        setSentIds((prev) => new Set(prev).add(key));
      } else {
        showToast('Erro ao registrar envio: ' + err.message, 'error');
        throw err;
      }
    }
  };

  // Filter groups by search term
  const filteredGrupos = useMemo(() => {
    if (!data || !data.grupos) return [];
    if (!busca.trim()) return data.grupos;

    const term = busca.toLowerCase();
    return data.grupos
      .map((grupo) => ({
        ...grupo,
        pendentes: grupo.pendentes.filter((p) =>
          p.cliente_nome.toLowerCase().includes(term)
        ),
        total: grupo.pendentes.filter((p) =>
          p.cliente_nome.toLowerCase().includes(term)
        ).length,
      }))
      .filter((grupo) => grupo.total > 0);
  }, [data, busca]);

  // Calculate totals
  const totalPendentes = data
    ? data.total_pendentes + data.total_enviados_hoje
    : 0;
  const totalEnviados = data ? data.total_enviados_hoje + sentIds.size : 0;

  if (loading) {
    return (
      <div className="loading-page">
        <div className="loading-spinner" />
      </div>
    );
  }

  return (
    <>
      <div className="page-header">
        <div className="page-header-row">
          <h1 className="page-header-title">Mensagens de hoje</h1>
          <div className="page-actions">
            <input
              className="search-input"
              type="text"
              placeholder="Buscar por nome..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
            />
          </div>
        </div>
      </div>

      {totalPendentes > 0 && (
        <ProgressBar enviados={totalEnviados} total={totalPendentes} />
      )}

      {filteredGrupos.length > 0 ? (
        filteredGrupos.map((grupo) => (
          <CampaignGroup
            key={grupo.campanha_id}
            grupo={grupo}
            onSend={handleSend}
            sentIds={sentIds}
          />
        ))
      ) : (
        <EmptyState />
      )}
    </>
  );
}
