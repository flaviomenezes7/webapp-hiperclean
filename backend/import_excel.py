"""
Script de importacao da planilha do Helsio para o banco do Hiper Clean CRM.

Logica:
1. Le todas as abas (2024, 2025, 2026)
2. Para cada linha com cliente valido:
   - Extrai nome (limpa horario, numero de cliente, anotacoes)
   - Extrai telefone (formata para 55DDDNUMERO se possivel)
   - Extrai aniversario
   - Extrai endereco
   - Extrai tipo de servico e data do atendimento
3. Deduplica clientes pelo telefone (mesmo telefone = mesmo cliente)
4. Insere clientes e atendimentos no banco SQLite
"""

import re
import sys
import uuid
from datetime import date, datetime
from pathlib import Path

import openpyxl

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, select
from app.database import engine, create_db_and_tables
from app.models.cliente import Cliente
from app.models.atendimento import Atendimento
from app.models.enums import TipoServico
import app.models  # noqa: F401 - register all models


EXCEL_PATH = r"C:\Users\mnzfl\Desktop\Helsio Excel.xlsx"

# --- Helpers ---

def clean_nome(raw: str) -> str | None:
    """
    Limpa o nome do cliente removendo horario, numero de ordem, 'cliente', etc.
    Exemplos:
      'Katia  08h30  1.196o cliente' -> 'Katia'
      'Raquel Gomes     14h          687a cliente' -> 'Raquel Gomes'
      'Cristiane e Luciano       08h30         942o clien' -> 'Cristiane e Luciano'
      'Mariana Lyra       08h30       (Vitor)     694o cl' -> 'Mariana Lyra'
    """
    if not raw or not raw.strip():
        return None

    text = raw.strip()

    # Skip non-client rows
    skip_patterns = [
        r'^F\s*O\s*L\s*G\s*A',
        r'^s[aá]bado',
        r'^domingo',
        r'^Viagem',
        r'^Manuten[cç][aã]o',
        r'^Cliente$',
        r'^Janeiro$', r'^Fevereiro$', r'^Mar[cç]o$', r'^Abril$', r'^Maio$',
        r'^Junho$', r'^Julho$', r'^Agosto$', r'^Setembro$', r'^Outubro$',
        r'^Novembro$', r'^Dezembro$',
        r'^Agenda de Clientes',
        r'^Oficina',
        r'^Helzio',
        r'^n[aã]o fez',
    ]
    for pattern in skip_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return None

    # Remove time patterns: 08h, 08h30, 14h, 09h30
    text = re.sub(r'\s+\d{1,2}h\d{0,2}\s*', ' ', text)

    # Remove client number: '1.196o cliente', '687a cliente', '942o clien', '694o cl'
    text = re.sub(r'\s+\d{1,2}\.\d{3}[oa\u00ba\u00aa]?\s*(cliente|clien|cl)\w*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+\d{3,4}[oa\u00ba\u00aa]?\s*(cliente|clien|cl)\w*', '', text, flags=re.IGNORECASE)

    # Remove parenthetical notes like (Reagendamos), (WhatsApp), (filha de bete), (Vitor)
    # But keep names in parens that look like part of the name
    text = re.sub(r'\s*\((?:Reagendamos|desmarcou|WhatsApp|mae\s|filha\s|o carpete|nao fez)[^)]*\)', '', text, flags=re.IGNORECASE)

    # Remove trailing annotations
    text = re.sub(r'\s+desmarcou.*$', '', text, flags=re.IGNORECASE)

    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # If too short or empty after cleaning, skip
    if len(text) < 2:
        return None

    return text


def clean_telefone(raw) -> str | None:
    """
    Limpa o telefone. Pode vir como:
      '99852-7526' (sem DDD)
      '31 98239-0439' (com DDD)
      '99833-7849         99829-4161' (dois numeros - pega o primeiro)
      '2141-8041' (fixo/comercial - pula)
    """
    if not raw:
        return None

    text = str(raw).strip()
    if not text:
        return None

    # Se tem dois numeros separados por espaco, pega o primeiro
    parts = re.split(r'\s{2,}', text)
    text = parts[0].strip()

    # Remove tudo exceto digitos
    digits = re.sub(r'\D', '', text)

    if len(digits) < 8:
        return None

    # Se ja tem 55 + DDD + numero (12-13 digitos), retorna
    if len(digits) >= 12 and digits.startswith('55'):
        return digits[:13]

    # Se tem DDD + numero (10-11 digitos)
    if len(digits) >= 10:
        return '55' + digits[:11]

    # Se so tem o numero sem DDD (8-9 digitos) - nao adiciona DDD
    if 8 <= len(digits) <= 9:
        return digits  # Sem DDD, vai precisar revisao manual

    return None


def parse_aniversario(raw) -> date | None:
    """Parseia data de aniversario. Pode vir como datetime ou string."""
    if raw is None:
        return None

    if isinstance(raw, datetime):
        # O ano pode ser fake (2021, 2023) - extrair so mes/dia
        return date(raw.year, raw.month, raw.day)

    text = str(raw).strip()
    if not text:
        return None

    # Formato '15-mar', '02-jun', etc.
    meses = {
        'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
        'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12,
    }
    match = re.match(r'(\d{1,2})[/-](\w{3})', text, re.IGNORECASE)
    if match:
        day = int(match.group(1))
        month_str = match.group(2).lower()
        month = meses.get(month_str)
        if month and 1 <= day <= 31:
            return date(2000, month, day)  # Ano placeholder

    return None


def classify_servico(descricao: str) -> TipoServico:
    """Classifica o tipo de servico baseado na descricao textual."""
    if not descricao:
        return TipoServico.OUTRO

    text = descricao.lower()

    if 'colch' in text:
        return TipoServico.COLCHAO
    if 'cadeira' in text:
        return TipoServico.CADEIRA
    if 'tapete' in text or 'carpete' in text:
        return TipoServico.TAPETE
    if 'cortina' in text:
        return TipoServico.CORTINA
    if 'poltrona' in text:
        return TipoServico.POLTRONA
    if 'banco' in text and ('carro' in text or 'veic' in text or 'automotivo' in text):
        return TipoServico.BANCO_AUTOMOTIVO
    if 'sof' in text:
        return TipoServico.SOFA
    if 'puff' in text or 'puf' in text:
        return TipoServico.SOFA

    return TipoServico.OUTRO


def parse_date(raw) -> date | None:
    """Parseia data da higienizacao."""
    if raw is None:
        return None

    if isinstance(raw, datetime):
        return raw.date()
    if isinstance(raw, date):
        return raw

    text = str(raw).strip()
    # Try 'sabado  06/01/2024' format
    match = re.search(r'(\d{2})/(\d{2})/(\d{4})', text)
    if match:
        try:
            return date(int(match.group(3)), int(match.group(2)), int(match.group(1)))
        except ValueError:
            pass

    return None


# --- Main import logic ---

def import_excel():
    """Le o Excel e importa para o banco."""
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)

    # Collect all raw records
    records = []

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        print(f"\n--- Processando aba: {sheet_name} ({ws.max_row} linhas) ---")

        for row in ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True):
            # Unpack columns A-G
            col_a = row[0] if len(row) > 0 else None
            col_b = row[1] if len(row) > 1 else None
            col_c = row[2] if len(row) > 2 else None
            col_d = row[3] if len(row) > 3 else None
            col_e = row[4] if len(row) > 4 else None
            col_f = row[5] if len(row) > 5 else None
            col_g = row[6] if len(row) > 6 else None

            nome = clean_nome(str(col_a) if col_a else "")
            if not nome:
                continue

            telefone = clean_telefone(col_e)
            aniversario = parse_aniversario(col_f)
            endereco = str(col_g).strip() if col_g else None
            data_atend = parse_date(col_c)
            tipo_servico = classify_servico(str(col_b) if col_b else "")
            descricao_servico = str(col_b).strip() if col_b else None

            records.append({
                'nome': nome,
                'telefone': telefone,
                'aniversario': aniversario,
                'endereco': endereco,
                'data_atend': data_atend,
                'tipo_servico': tipo_servico,
                'descricao_servico': descricao_servico,
                'aba': sheet_name,
            })

    print(f"\n=== Total de registros brutos: {len(records)} ===")

    # Deduplicate clients by phone (same phone = same person)
    # For clients without phone, deduplicate by name
    clientes_map = {}  # key -> {nome, telefone, aniversario, endereco, atendimentos: []}

    for rec in records:
        # Build dedup key
        if rec['telefone'] and len(rec['telefone']) >= 8:
            key = rec['telefone'][-8:]  # Last 8 digits
        else:
            key = rec['nome'].lower().strip()

        if key not in clientes_map:
            clientes_map[key] = {
                'nome': rec['nome'],
                'telefone': rec['telefone'],
                'aniversario': rec['aniversario'],
                'endereco': rec['endereco'],
                'atendimentos': [],
            }
        else:
            # Update with more complete data if available
            existing = clientes_map[key]
            if not existing['telefone'] and rec['telefone']:
                existing['telefone'] = rec['telefone']
            if not existing['aniversario'] and rec['aniversario']:
                existing['aniversario'] = rec['aniversario']
            if not existing['endereco'] and rec['endereco']:
                existing['endereco'] = rec['endereco']

        if rec['data_atend']:
            clientes_map[key]['atendimentos'].append({
                'data_atend': rec['data_atend'],
                'tipo_servico': rec['tipo_servico'],
                'descricao_servico': rec['descricao_servico'],
            })

    print(f"Clientes unicos: {len(clientes_map)}")

    # Count stats
    com_telefone = sum(1 for c in clientes_map.values() if c['telefone'])
    sem_telefone = sum(1 for c in clientes_map.values() if not c['telefone'])
    com_telefone_completo = sum(1 for c in clientes_map.values() if c['telefone'] and len(c['telefone']) >= 12)
    com_telefone_sem_ddd = sum(1 for c in clientes_map.values() if c['telefone'] and len(c['telefone']) < 12)
    total_atendimentos = sum(len(c['atendimentos']) for c in clientes_map.values())

    print(f"  Com telefone completo (55+DDD): {com_telefone_completo}")
    print(f"  Com telefone sem DDD: {com_telefone_sem_ddd}")
    print(f"  Sem telefone: {sem_telefone}")
    print(f"  Total de atendimentos: {total_atendimentos}")

    # Insert into database
    create_db_and_tables()

    with Session(engine) as session:
        # Clear ALL existing data (demo + any previous import)
        from app.models.envio import Envio
        envios = session.exec(select(Envio)).all()
        for e in envios:
            session.delete(e)

        atends_existing = session.exec(select(Atendimento)).all()
        for a in atends_existing:
            session.delete(a)

        existing_clients = session.exec(select(Cliente)).all()
        if existing_clients:
            print(f"\nRemovendo {len(existing_clients)} clientes existentes...")
            for c in existing_clients:
                session.delete(c)

        session.commit()

        clientes_inseridos = 0
        atendimentos_inseridos = 0
        problemas = []

        for key, data in clientes_map.items():
            telefone = data['telefone']

            # Skip clients without any useful contact info
            if not telefone:
                problemas.append(f"SEM TELEFONE: {data['nome']}")
                # Still insert, but without phone
                telefone = None

            cliente = Cliente(
                nome=data['nome'],
                telefone=telefone or "",
                data_nasc=data['aniversario'],
                endereco=data['endereco'],
            )
            session.add(cliente)
            session.flush()  # Get the ID
            clientes_inseridos += 1

            # Insert atendimentos
            for atend in data['atendimentos']:
                atendimento = Atendimento(
                    cliente_id=cliente.id,
                    tipo_servico=atend['tipo_servico'],
                    data_atend=atend['data_atend'],
                    observacoes=atend['descricao_servico'],
                )
                session.add(atendimento)
                atendimentos_inseridos += 1

        session.commit()

    print(f"\n{'='*50}")
    print(f"IMPORTACAO CONCLUIDA!")
    print(f"  Clientes inseridos: {clientes_inseridos}")
    print(f"  Atendimentos inseridos: {atendimentos_inseridos}")

    if problemas:
        print(f"\n  Problemas ({len(problemas)}):")
        for p in problemas[:20]:
            print(f"    - {p}")
        if len(problemas) > 20:
            print(f"    ... e mais {len(problemas) - 20}")

    print(f"\nClientes SEM DDD (precisam revisao manual): {com_telefone_sem_ddd}")
    if com_telefone_sem_ddd > 0:
        print("  -> Edite esses clientes no app e adicione o DDD+55 antes do numero")


if __name__ == "__main__":
    import_excel()
