"""Database models."""

from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.sql import func
from data.database import Base


class Circulating(Base):
    """Model for storing circulating supply data."""

    __tablename__ = "circulating"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    gecko_id = Column(String, nullable=False)
    peg_type = Column(String, nullable=False)
    peg_mechanism = Column(String, nullable=False)
    chain = Column(String, nullable=False)
    supply = Column(Float, nullable=False)
    change_24h = Column(Float)
    change_7d = Column(Float)
    change_30d = Column(Float)
    price = Column(Float)

    # Create indexes
    __table_args__ = (
        Index("ix_circulating_timestamp", "timestamp"),
        Index("ix_circulating_symbol", "symbol"),
        Index("ix_circulating_chain", "chain"),
    )

    def __repr__(self):
        return f"<Circulating(symbol={self.symbol}, chain={self.chain}, supply={self.supply})>"
