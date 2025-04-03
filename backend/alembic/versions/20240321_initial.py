"""initial

Revision ID: 20240321
Revises:
Create Date: 2024-03-21 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20240321"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "circulating",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("gecko_id", sa.String(), nullable=False),
        sa.Column("peg_type", sa.String(), nullable=False),
        sa.Column("peg_mechanism", sa.String(), nullable=False),
        sa.Column("chain", sa.String(), nullable=False),
        sa.Column("supply", sa.Float(), nullable=False),
        sa.Column("price", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_circulating_timestamp", "circulating", ["timestamp"])
    op.create_index("ix_circulating_symbol", "circulating", ["symbol"])
    op.create_index("ix_circulating_chain", "circulating", ["chain"])


def downgrade():
    op.drop_table("circulating")
