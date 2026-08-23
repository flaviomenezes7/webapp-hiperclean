"""Verifica os dados importados no banco."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, select, func
from app.database import engine
from app.models.cliente import Cliente
from app.models.atendimento import Atendimento
import app.models  # noqa

with Session(engine) as session:
    total_clientes = session.exec(select(func.count()).select_from(Cliente)).one()
    total_atend = session.exec(select(func.count()).select_from(Atendimento)).one()

    # Phone stats
    com_ddd = 0
    sem_ddd = 0
    for c in session.exec(select(Cliente)).all():
        if c.telefone and len(c.telefone) >= 12:
            com_ddd += 1
        elif c.telefone:
            sem_ddd += 1

    # Birthday stats
    com_aniv = session.exec(
        select(func.count()).select_from(Cliente).where(Cliente.data_nasc.isnot(None))
    ).one()

    print(f"=== RESUMO DA IMPORTACAO ===")
    print(f"Total clientes: {total_clientes}")
    print(f"Total atendimentos: {total_atend}")
    print(f"")
    print(f"Telefones:")
    print(f"  Com DDD completo (55+DDD+num): {com_ddd}")
    print(f"  Sem DDD (so numero local): {sem_ddd}")
    print(f"")
    print(f"Com aniversario cadastrado: {com_aniv}")
    print(f"")
    print(f"--- Primeiros 10 clientes ---")
    clientes = session.exec(select(Cliente).limit(10)).all()
    for c in clientes:
        tel_status = "OK" if c.telefone and len(c.telefone) >= 12 else "SEM DDD" if c.telefone else "SEM TEL"
        aniv = c.data_nasc.strftime("%d/%m") if c.data_nasc else "-"
        print(f"  {c.nome:30s} | tel: {c.telefone:15s} [{tel_status}] | aniv: {aniv}")
