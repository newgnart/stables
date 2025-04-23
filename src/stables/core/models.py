"""Database models."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Index,
    ForeignKey,
    UniqueConstraint,
    ForeignKeyConstraint,
)
from sqlalchemy.sql import func
from stables.core.database import Base


class LlamaStable(Base):
    """Model for storing stablecoin metadata and total circulating supply."""

    __tablename__ = "llama_stable"

    # Primary key columns
    id = Column(String, primary_key=True)
    time_utc = Column(DateTime, primary_key=True)

    # Data columns
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    gecko_id = Column(String, nullable=False)
    peg_type = Column(String, nullable=False)
    peg_mechanism = Column(String, nullable=False)
    total_circulating = Column(Float, nullable=False)

    # Create index for time-based queries
    __table_args__ = (Index("ix_llama_stable_time_utc", "time_utc"),)

    def __repr__(self):
        """Return a string representation of the LlamaStable object."""
        return (
            f"<LlamaStable("
            f"id='{self.id}', "
            f"symbol='{self.symbol}', "
            f"name='{self.name}', "
            f"peg_type='{self.peg_type}', "
            f"total_circulating={self.total_circulating:.2f}, "
            f"time_utc='{self.time_utc}')"
            ">"
        )

    def __str__(self):
        """Return a user-friendly string representation."""
        return (
            f"{self.symbol} ({self.name}): {self.total_circulating:.2f} {self.peg_type}"
        )


class LlamaChainCirculating(Base):
    """Model for storing chain-specific circulating supply data."""

    __tablename__ = "llama_chain_circulating"

    # Primary key columns in optimal order
    stable_id = Column(String, primary_key=True)
    time_utc = Column(DateTime, primary_key=True)
    chain = Column(String, primary_key=True)

    # Data column
    circulating = Column(Float, nullable=False)

    # Create composite foreign key and index
    __table_args__ = (
        ForeignKeyConstraint(
            ["stable_id", "time_utc"],
            ["llama_stable.id", "llama_stable.time_utc"],
            name="fk_chain_circulating_stable",
        ),
        Index("ix_llama_chain_circulating_time_chain", "time_utc", "chain"),
    )

    def __repr__(self):
        """Return a string representation of the LlamaChainCirculating object."""
        return (
            f"<LlamaChainCirculating("
            f"stable_id='{self.stable_id}', "
            f"chain='{self.chain}', "
            f"circulating={self.circulating:.2f}, "
            f"time_utc='{self.time_utc}')"
            ">"
        )

    def __str__(self):
        """Return a user-friendly string representation."""
        return f"{self.chain}: {self.circulating:.2f}"
