import enum


class TipoServico(str, enum.Enum):
    """Tipos de serviço de limpeza oferecidos."""
    SOFA = "SOFA"
    COLCHAO = "COLCHAO"
    CADEIRA = "CADEIRA"
    TAPETE = "TAPETE"
    CORTINA = "CORTINA"
    POLTRONA = "POLTRONA"
    BANCO_AUTOMOTIVO = "BANCO_AUTOMOTIVO"
    OUTRO = "OUTRO"


class TipoGatilho(str, enum.Enum):
    """Tipos de gatilho para regras de campanha."""
    ANIVERSARIO = "ANIVERSARIO"                # Aniversário do cliente
    DIAS_APOS_ATENDIMENTO = "DIAS_APOS_ATENDIMENTO"  # N dias após atendimento
    DATA_FIXA = "DATA_FIXA"                    # Data fixa no calendário (Natal, Páscoa, etc.)
