"""Create llama_stable and llama_chain_circulating tables.

Revision ID: 20240404_stables
Revises:
Create Date: 2024-04-04 10:40:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20240404_stables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create llama_stable table with optimized structure
    op.create_table(
        "llama_stable",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("gecko_id", sa.String(), nullable=False),
        sa.Column("peg_type", sa.String(), nullable=False),
        sa.Column("peg_mechanism", sa.String(), nullable=False),
        sa.Column("total_circulating", sa.Float(), nullable=False),
        sa.Column(
            "time_utc",
            sa.DateTime(),  # Store without timezone since we handle UTC in app
            server_default=sa.text("TIMEZONE('UTC', NOW())"),
            nullable=False,
        ),
        # Primary key order matters for performance:
        # id first for foreign key references
        # time_utc second for time-based queries
        sa.PrimaryKeyConstraint("id", "time_utc"),
    )

    # Create indexes for llama_stable table
    # No need for symbol/gecko_id indexes unless you frequently query by them
    op.create_index("ix_llama_stable_time_utc", "llama_stable", ["time_utc"])

    # Create llama_chain_circulating table with optimized structure
    op.create_table(
        "llama_chain_circulating",
        sa.Column("stable_id", sa.String(), nullable=False),
        sa.Column("chain", sa.String(), nullable=False),
        sa.Column("circulating", sa.Float(), nullable=False),
        sa.Column(
            "time_utc",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('UTC', NOW())"),
            nullable=False,
        ),
        # Foreign key to reference the current stablecoin metadata
        sa.ForeignKeyConstraint(
            ["stable_id", "time_utc"],  # Composite foreign key
            ["llama_stable.id", "llama_stable.time_utc"],
            name="fk_chain_circulating_stable",
            # Add ondelete="CASCADE" if you want automatic deletion
        ),
        # Primary key order optimized for queries:
        # stable_id first for joining with llama_stable
        # time_utc second for time-based queries
        # chain last as it's mostly used for filtering
        sa.PrimaryKeyConstraint("stable_id", "time_utc", "chain"),
    )

    # Create selective indexes for common query patterns
    op.create_index(
        "ix_llama_chain_circulating_time_chain",
        "llama_chain_circulating",
        ["time_utc", "chain"],  # Composite index for time+chain queries
    )


def downgrade():
    # Drop indexes first
    op.drop_index(
        "ix_llama_chain_circulating_time_chain", table_name="llama_chain_circulating"
    )
    op.drop_index("ix_llama_stable_time_utc", table_name="llama_stable")

    # Drop tables
    op.drop_table("llama_chain_circulating")
    op.drop_table("llama_stable")
