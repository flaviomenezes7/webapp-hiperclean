"""
Serviço de cálculo on-the-fly dos pendentes de hoje.

Para cada regra de campanha ativa, calcula quais clientes precisam ser
contactados hoje e monta a mensagem pré-preenchida com link wa.me.
"""

import uuid
from datetime import date, timedelta
from urllib.parse import quote

from sqlmodel import Session, select, col
from sqlalchemy import and_, extract, func

from app.models.cliente import Cliente
from app.models.atendimento import Atendimento
from app.models.campanha import RegraCampanha
from app.models.envio import Envio
from app.models.enums import TipoGatilho, TipoServico
from app.schemas.pendente import (
    PendenteItem,
    CampanhaGroup,
    PendentesHojeResponse,
)


# Human-readable labels for TipoServico
SERVICO_LABELS: dict[TipoServico, str] = {
    TipoServico.SOFA: "sofá",
    TipoServico.COLCHAO: "colchão",
    TipoServico.CADEIRA: "cadeira",
    TipoServico.TAPETE: "tapete",
    TipoServico.CORTINA: "cortina",
    TipoServico.POLTRONA: "poltrona",
    TipoServico.BANCO_AUTOMOTIVO: "banco automotivo",
    TipoServico.OUTRO: "estofado",
}


def _get_iniciais(nome: str) -> str:
    """Extrai iniciais do nome (máx 2 caracteres)."""
    partes = nome.strip().split()
    if len(partes) >= 2:
        return (partes[0][0] + partes[-1][0]).upper()
    return nome[0:2].upper()


def _build_whatsapp_link(telefone: str, mensagem: str) -> str:
    """Monta link wa.me com texto pré-preenchido."""
    return f"https://wa.me/{telefone}?text={quote(mensagem)}"


def _format_template(
    template: str,
    nome: str,
    dias: int | None = None,
    servico: str | None = None,
) -> str:
    """
    Substitui placeholders no template da campanha.
    Placeholders suportados: {nome}, {dias}, {servico}
    """
    msg = template.replace("{nome}", nome)
    if dias is not None:
        msg = msg.replace("{dias}", str(dias))
    if servico is not None:
        msg = msg.replace("{servico}", servico)
    return msg


def _get_pendentes_aniversario(
    session: Session,
    campanha: RegraCampanha,
    hoje: date,
) -> list[PendenteItem]:
    """
    Clientes cujo mês/dia de nascimento = hoje,
    excluindo os que já tiveram envio neste ano para esta campanha.
    """
    referencia = date(hoje.year, hoje.month, hoje.day)

    # Subquery: clientes que já receberam envio desta campanha com referencia_data neste ano
    enviados_subq = (
        select(Envio.cliente_id)
        .where(
            Envio.campanha_id == campanha.id,
            Envio.referencia_data == referencia,
        )
    )

    stmt = (
        select(Cliente)
        .where(
            Cliente.deleted_at.is_(None),  # type: ignore
            Cliente.data_nasc.is_not(None),  # type: ignore
            extract("month", Cliente.data_nasc) == hoje.month,
            extract("day", Cliente.data_nasc) == hoje.day,
            col(Cliente.id).notin_(enviados_subq),
        )
    )

    clientes = session.exec(stmt).all()
    items = []
    for c in clientes:
        msg = _format_template(campanha.template_msg, c.nome)
        items.append(
            PendenteItem(
                cliente_id=c.id,
                cliente_nome=c.nome,
                cliente_telefone=c.telefone,
                cliente_iniciais=_get_iniciais(c.nome),
                campanha_id=campanha.id,
                referencia_data=referencia,
                mensagem_formatada=msg,
                link_whatsapp=_build_whatsapp_link(c.telefone, msg),
            )
        )
    return items


def _get_pendentes_dias_apos_atendimento(
    session: Session,
    campanha: RegraCampanha,
    hoje: date,
) -> list[PendenteItem]:
    """
    Atendimentos cuja data_atend + dias_offset <= hoje (ou seja, já
    completaram os N dias ou mais), excluindo os que já tiveram envio
    registrado para aquele atendimento+campanha.

    Usa data_atend como referencia_data no envio, para rastrear cada
    atendimento individualmente.
    """
    if campanha.dias_offset is None:
        return []

    # Data limite: atendimentos feitos até esta data já "venceram"
    data_limite = hoje - timedelta(days=campanha.dias_offset)

    # Subquery: envios já feitos para esta campanha.
    # Cada envio tem referencia_data = data_atend do atendimento que o gerou.
    # Usamos (cliente_id, referencia_data) para identificar univocamente.
    enviados_subq = (
        select(Envio.cliente_id, Envio.referencia_data)
        .where(Envio.campanha_id == campanha.id)
        .subquery()
    )

    stmt = (
        select(Atendimento, Cliente)
        .join(Cliente, Atendimento.cliente_id == Cliente.id)
        .outerjoin(
            enviados_subq,
            and_(
                Atendimento.cliente_id == enviados_subq.c.cliente_id,
                Atendimento.data_atend == enviados_subq.c.referencia_data,
            ),
        )
        .where(
            Cliente.deleted_at.is_(None),  # type: ignore
            Atendimento.data_atend <= data_limite,
            enviados_subq.c.cliente_id.is_(None),  # Não tem envio registrado
        )
    )

    results = session.exec(stmt).all()
    items = []
    seen = set()  # Evitar duplicatas (mesmo cliente, múltiplos atendimentos)
    for atend, cliente in results:
        # Usar (cliente_id, data_atend) como chave única
        key = (str(cliente.id), str(atend.data_atend))
        if key in seen:
            continue
        seen.add(key)

        dias_passados = (hoje - atend.data_atend).days
        servico_label = SERVICO_LABELS.get(atend.tipo_servico, "estofado")
        msg = _format_template(
            campanha.template_msg,
            cliente.nome,
            dias=dias_passados,
            servico=servico_label,
        )
        items.append(
            PendenteItem(
                cliente_id=cliente.id,
                cliente_nome=cliente.nome,
                cliente_telefone=cliente.telefone,
                cliente_iniciais=_get_iniciais(cliente.nome),
                campanha_id=campanha.id,
                referencia_data=atend.data_atend,
                mensagem_formatada=msg,
                link_whatsapp=_build_whatsapp_link(cliente.telefone, msg),
            )
        )
    return items


def _get_pendentes_data_fixa(
    session: Session,
    campanha: RegraCampanha,
    hoje: date,
) -> list[PendenteItem]:
    """
    Se hoje = mes_fixo/dia_fixo da campanha, retorna TODOS os clientes ativos
    que ainda não receberam envio desta campanha neste ano.
    """
    if campanha.mes_fixo is None or campanha.dia_fixo is None:
        return []

    if hoje.month != campanha.mes_fixo or hoje.day != campanha.dia_fixo:
        return []

    referencia = date(hoje.year, campanha.mes_fixo, campanha.dia_fixo)

    enviados_subq = (
        select(Envio.cliente_id)
        .where(
            Envio.campanha_id == campanha.id,
            Envio.referencia_data == referencia,
        )
    )

    stmt = (
        select(Cliente)
        .where(
            Cliente.deleted_at.is_(None),  # type: ignore
            col(Cliente.id).notin_(enviados_subq),
        )
    )

    clientes = session.exec(stmt).all()
    items = []
    for c in clientes:
        msg = _format_template(campanha.template_msg, c.nome)
        items.append(
            PendenteItem(
                cliente_id=c.id,
                cliente_nome=c.nome,
                cliente_telefone=c.telefone,
                cliente_iniciais=_get_iniciais(c.nome),
                campanha_id=campanha.id,
                referencia_data=referencia,
                mensagem_formatada=msg,
                link_whatsapp=_build_whatsapp_link(c.telefone, msg),
            )
        )
    return items


def get_pendentes_hoje(session: Session, hoje: date | None = None) -> PendentesHojeResponse:
    """
    Calcula on-the-fly todos os pendentes de hoje, agrupados por campanha.
    """
    if hoje is None:
        hoje = date.today()

    # Fetch all active campaigns
    campanhas = session.exec(
        select(RegraCampanha).where(RegraCampanha.ativa == True)  # noqa: E712
    ).all()

    grupos: list[CampanhaGroup] = []
    total_pendentes = 0

    for campanha in campanhas:
        if campanha.tipo_gatilho == TipoGatilho.ANIVERSARIO:
            pendentes = _get_pendentes_aniversario(session, campanha, hoje)
        elif campanha.tipo_gatilho == TipoGatilho.DIAS_APOS_ATENDIMENTO:
            pendentes = _get_pendentes_dias_apos_atendimento(session, campanha, hoje)
        elif campanha.tipo_gatilho == TipoGatilho.DATA_FIXA:
            pendentes = _get_pendentes_data_fixa(session, campanha, hoje)
        else:
            pendentes = []

        if pendentes:
            grupos.append(
                CampanhaGroup(
                    campanha_id=campanha.id,
                    campanha_nome=campanha.nome,
                    campanha_emoji=campanha.emoji,
                    tipo_gatilho=campanha.tipo_gatilho,
                    pendentes=pendentes,
                    total=len(pendentes),
                )
            )
            total_pendentes += len(pendentes)

    # Count how many were already sent today (across all campaigns)
    total_enviados_hoje = session.exec(
        select(func.count())
        .select_from(Envio)
        .where(func.date(Envio.enviado_em) == hoje)
    ).one()

    return PendentesHojeResponse(
        data=hoje,
        grupos=grupos,
        total_pendentes=total_pendentes,
        total_enviados_hoje=total_enviados_hoje,
    )
