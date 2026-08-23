from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from app.config import get_settings
from app.auth import authenticate_user, create_access_token, Token
from app.database import create_db_and_tables, is_sqlite
from app.routers import clientes, atendimentos, campanhas, pendentes, envios

settings = get_settings()


def seed_demo_data():
    """Insere dados de demonstração no primeiro boot (somente SQLite/local)."""
    from app.database import engine
    from sqlmodel import Session, select
    from app.models.campanha import RegraCampanha
    from app.models.cliente import Cliente
    from app.models.atendimento import Atendimento
    from app.models.enums import TipoGatilho, TipoServico
    from datetime import date, timedelta

    with Session(engine) as session:
        # Só faz seed se não existir nenhuma campanha
        existing = session.exec(select(RegraCampanha)).first()
        if existing:
            return

        # --- Campanhas ---
        c1 = RegraCampanha(
            nome="Aniversário",
            emoji="🎂",
            tipo_gatilho=TipoGatilho.ANIVERSARIO,
            template_msg="Feliz aniversário, {nome}! 🎂 A Hiper Clean deseja um dia incrível! Que tal comemorar com estofados limpinhos? Temos uma condição especial para você!",
            ativa=True,
        )
        c2 = RegraCampanha(
            nome="Lembrete de limpeza",
            emoji="🕐",
            tipo_gatilho=TipoGatilho.DIAS_APOS_ATENDIMENTO,
            dias_offset=180,
            template_msg="Olá, {nome}! Já faz {dias} dias que limpamos seu {servico}. Que tal agendar uma nova limpeza? Entre em contato e agende o melhor dia! 🧹✨",
            ativa=True,
        )
        c3 = RegraCampanha(
            nome="Natal",
            emoji="🎄",
            tipo_gatilho=TipoGatilho.DATA_FIXA,
            mes_fixo=12,
            dia_fixo=25,
            template_msg="🎄 Feliz Natal, {nome}! A Hiper Clean deseja boas festas! Comece o ano novo com a casa limpinha — agende sua limpeza de estofados!",
            ativa=True,
        )
        session.add_all([c1, c2, c3])

        # --- Clientes demo ---
        hoje = date.today()
        cl1 = Cliente(nome="Maria Oliveira", telefone="5511999887766", data_nasc=date(1990, hoje.month, hoje.day))
        cl2 = Cliente(nome="João Santos", telefone="5511988776655", data_nasc=date(1985, hoje.month, hoje.day))
        cl3 = Cliente(nome="Ana Costa", telefone="5521977665544", data_nasc=date(1992, hoje.month, hoje.day))
        cl4 = Cliente(nome="Carlos Pereira", telefone="5511966554433", data_nasc=date(1988, 3, 15))
        cl5 = Cliente(nome="Fernanda Lima", telefone="5521955443322", data_nasc=date(1995, 7, 20))
        cl6 = Cliente(nome="Ricardo Alves", telefone="5511944332211", data_nasc=date(1980, 11, 5))
        cl7 = Cliente(nome="Juliana Rocha", telefone="5511933221100", data_nasc=date(1993, 1, 28))
        session.add_all([cl1, cl2, cl3, cl4, cl5, cl6, cl7])
        session.flush()

        # --- Atendimentos (180 dias atrás → vão aparecer hoje como "lembrete") ---
        data_180_atras = hoje - timedelta(days=180)
        at1 = Atendimento(cliente_id=cl4.id, tipo_servico=TipoServico.SOFA, data_atend=data_180_atras)
        at2 = Atendimento(cliente_id=cl5.id, tipo_servico=TipoServico.COLCHAO, data_atend=data_180_atras)
        at3 = Atendimento(cliente_id=cl6.id, tipo_servico=TipoServico.TAPETE, data_atend=data_180_atras)
        at4 = Atendimento(cliente_id=cl7.id, tipo_servico=TipoServico.SOFA, data_atend=data_180_atras)
        session.add_all([at1, at2, at3, at4])

        session.commit()
        print("[OK] Dados de demonstracao inseridos com sucesso!")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables (SQLite) and seed demo data."""
    if is_sqlite:
        # Import models so SQLModel sees them
        import app.models  # noqa: F811, F401
        create_db_and_tables()
        seed_demo_data()
    yield


app = FastAPI(
    title="Hiper Clean CRM",
    description="Sistema de CRM para gestão de relacionamento com clientes — Hiper Clean Limpeza de Estofados",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend (Vercel) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth endpoint ---
@app.post("/auth/login", response_model=Token, tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login com email e senha. Retorna um JWT Bearer token.
    Use o campo 'username' para o email (padrão OAuth2).
    """
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})
    return Token(access_token=access_token, token_type="bearer")


# --- Health check ---
@app.get("/health", tags=["Health"])
def health():
    """Health check endpoint for UptimeRobot / Render."""
    return {"status": "ok", "service": "hiper-clean-crm"}


# --- Include routers ---
app.include_router(clientes.router)
app.include_router(atendimentos.router)
app.include_router(campanhas.router)
app.include_router(pendentes.router)
app.include_router(envios.router)
