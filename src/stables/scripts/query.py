# Assuming you have a database session
from sqlalchemy.orm import Session
from core.models import LlamaStable, LlamaChainCirculating

# Example 1: Get a single stablecoin by ID and time
stable = (
    db.query(LlamaStable)
    .filter(LlamaStable.id == "USDT", LlamaStable.time_utc == some_time)
    .first()
)

# Now you can use the object and its __str__ or __repr__
print(stable)  # Uses __str__: "USDT (Tether): 1000000.00 USD"
print(f"Debug info: {stable!r}")  # Uses __repr__: "<LlamaStable(id='USDT', ...)>"

# Example 2: Get all records for a stablecoin
usdt_records = (
    db.query(LlamaStable)
    .filter(LlamaStable.id == "USDT")
    .order_by(LlamaStable.time_utc.desc())
    .all()
)

for record in usdt_records:
    print(f"Supply at {record.time_utc}: {record.total_circulating:.2f}")

# Example 3: Get latest record for each stablecoin
from sqlalchemy import func

latest_records = (
    db.query(LlamaStable)
    .filter(
        LlamaStable.time_utc
        == db.query(func.max(LlamaStable.time_utc))
        .filter(LlamaStable.id == LlamaStable.id)
        .scalar_subquery()
    )
    .all()
)

for record in latest_records:
    print(record)  # Uses __str__ for each record

# Example 4: Join with chain_circulating to get distribution
chain_data = (
    db.query(LlamaStable, LlamaChainCirculating)
    .join(
        LlamaChainCirculating,
        (LlamaStable.id == LlamaChainCirculating.stable_id)
        & (LlamaStable.time_utc == LlamaChainCirculating.time_utc),
    )
    .filter(LlamaStable.id == "USDT")
    .all()
)

for stable, chain in chain_data:
    print(f"{stable.symbol} on {chain.chain}: {chain.circulating:.2f}")
