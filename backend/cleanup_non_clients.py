"""Remove registros que nao sao clientes reais (feriados, viagens, anotacoes pessoais)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, select
from app.database import engine
from app.models.cliente import Cliente
from app.models.atendimento import Atendimento
import app.models  # noqa

with Session(engine) as session:
    # Find clients without phone (these are likely not real clients)
    clientes = session.exec(select(Cliente).where(Cliente.telefone == "")).all()

    removed = 0
    for c in clientes:
        # Delete atendimentos
        atends = session.exec(select(Atendimento).where(Atendimento.cliente_id == c.id)).all()
        for a in atends:
            session.delete(a)
        session.delete(c)
        removed += 1

    session.commit()
    print(f"Removidos {removed} registros sem telefone (nao sao clientes reais)")

    # Count remaining
    total = session.exec(select(Cliente)).all()
    print(f"Clientes restantes: {len(total)}")
