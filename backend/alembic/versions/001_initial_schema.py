"""Initial schema - create all tables

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-09-06
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- clientes ---
    op.create_table(
        "clientes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("telefone", sa.String(20), nullable=False),
        sa.Column("data_nasc", sa.Date(), nullable=True),
        sa.Column("endereco", sa.Text(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_clientes_telefone"), "clientes", ["telefone"])
    op.create_index(op.f("ix_clientes_data_nasc"), "clientes", ["data_nasc"])
    op.create_index(op.f("ix_clientes_deleted_at"), "clientes", ["deleted_at"])

    # --- regras_campanha ---
    op.create_table(
        "regras_campanha",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("emoji", sa.String(10), nullable=True),
        sa.Column("tipo_gatilho", sa.String(30), nullable=False),
        sa.Column("dias_offset", sa.Integer(), nullable=True),
        sa.Column("mes_fixo", sa.SmallInteger(), nullable=True),
        sa.Column("dia_fixo", sa.SmallInteger(), nullable=True),
        sa.Column("template_msg", sa.Text(), nullable=False),
        sa.Column(
            "ativa",
            sa.Boolean(),
            server_default="true",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_regras_campanha_tipo_gatilho"), "regras_campanha", ["tipo_gatilho"])
    op.create_index(op.f("ix_regras_campanha_ativa"), "regras_campanha", ["ativa"])

    # --- atendimentos ---
    op.create_table(
        "atendimentos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("cliente_id", sa.Uuid(), nullable=False),
        sa.Column("tipo_servico", sa.String(30), nullable=False),
        sa.Column("data_atend", sa.Date(), nullable=False),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("valor", sa.Numeric(10, 2), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"]),
    )
    op.create_index(op.f("ix_atendimentos_cliente_id"), "atendimentos", ["cliente_id"])
    op.create_index(op.f("ix_atendimentos_data_atend"), "atendimentos", ["data_atend"])

    # --- envios ---
    op.create_table(
        "envios",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("cliente_id", sa.Uuid(), nullable=False),
        sa.Column("campanha_id", sa.Uuid(), nullable=False),
        sa.Column("referencia_data", sa.Date(), nullable=False),
        sa.Column(
            "enviado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"]),
        sa.ForeignKeyConstraint(["campanha_id"], ["regras_campanha.id"]),
        sa.UniqueConstraint(
            "cliente_id",
            "campanha_id",
            "referencia_data",
            name="uq_envio_cliente_campanha_ref",
        ),
    )
    op.create_index(op.f("ix_envios_cliente_id"), "envios", ["cliente_id"])
    op.create_index(op.f("ix_envios_campanha_id"), "envios", ["campanha_id"])


def downgrade() -> None:
    op.drop_table("envios")
    op.drop_table("atendimentos")
    op.drop_table("regras_campanha")
    op.drop_table("clientes")
