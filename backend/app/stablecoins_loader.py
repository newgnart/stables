import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Stablecoin, Chain
from app.database import SessionLocal


def load_stablecoins(db: Session, json_path: Path) -> None:
    """Load stablecoins and chains from JSON file into database."""
    with open(json_path) as f:
        data = json.load(f)

    # Load chains first
    for chain_data in data["chains"]:
        chain = Chain(
            name=chain_data["name"],
            chain_id=chain_data["chain_id"],
            rpc_url=chain_data["rpc_url"],
        )
        db.merge(chain)  # merge will update if exists, insert if not

    # Load stablecoins
    for coin_data in data["stablecoins"]:
        coin = Stablecoin(
            symbol=coin_data["symbol"],
            name=coin_data["name"],
            decimals=coin_data["decimals"],
            type=coin_data["type"],
            addresses=coin_data["addresses"],
        )
        db.merge(coin)

    db.commit()


def main():
    """Main function to run the loader."""
    json_path = Path(__file__).parent / "data" / "stablecoins.json"
    if not json_path.exists():
        raise FileNotFoundError(f"Stablecoins JSON file not found at {json_path}")

    db = SessionLocal()
    try:
        load_stablecoins(db, json_path)
        print("Successfully loaded stablecoins and chains into database")
    except Exception as e:
        print(f"Error loading stablecoins: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
