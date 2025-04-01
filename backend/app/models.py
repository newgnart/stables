from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Stablecoin(Base):
    __tablename__ = "stablecoins"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    decimals = Column(Integer)
    type = Column(String)
    addresses = Column(JSON)  # Store addresses as JSON for different chains
    created_at = Column(DateTime, default=datetime.utcnow)
    contract_address = Column(String, nullable=False)
    chain_id = Column(Integer, ForeignKey("chains.id"), nullable=False)
    chain = relationship("Chain", back_populates="stablecoins")


class Chain(Base):
    __tablename__ = "chains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    chain_id = Column(Integer, unique=True)
    rpc_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    stablecoins = relationship("Stablecoin", back_populates="chain")


class AggregatedMetrics(Base):
    __tablename__ = "aggregated_metrics"

    id = Column(Integer, primary_key=True)
    stablecoin_id = Column(Integer, ForeignKey("stablecoins.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    total_transfer_volume = Column(Float, nullable=False)
    transfer_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
