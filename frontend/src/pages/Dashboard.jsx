import { useState, useEffect, useCallback } from 'react';
import api from '../api/client';
import Header from '../components/Header';
import ProgressBar from '../components/ProgressBar';
import CampaignGroup from '../components/CampaignGroup';
import EmptyState from '../components/EmptyState';

export default function Dashboard({ showToast }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sentIds, setSentIds] = useState(new Set());

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
      <Header title="Mensagens de hoje" />

      {totalPendentes > 0 && (
        <ProgressBar enviados={totalEnviados} total={totalPendentes} />
      )}

      {data && data.grupos.length > 0 ? (
        data.grupos.map((grupo) => (
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
