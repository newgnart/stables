"""ABI management for loading and caching contract ABIs."""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from stables.data.source.block_explorer import BlockExplorer
from .config import ABI_DIR
from .decoder import get_events
from .types import EventDefinition

logger = logging.getLogger(__name__)


class ABIManager:
    """Manages ABI loading, caching, and fetching for contracts."""
    
    def __init__(self, api_key: Optional[str] = None, chain_name: str = "mainnet"):
        """Initialize ABI manager."""
        self.api_key = api_key
        self.chain_name = chain_name
        self.block_explorer = None
        if api_key:
            self.block_explorer = BlockExplorer(api_key=api_key, chain_name=chain_name)
        
        self._events_cache: Dict[str, EventDefinition] = {}
        self._loaded_contracts: Set[str] = set()
    
    def get_all_contract_addresses(self, df_path: str) -> Set[str]:
        """Extract all unique contract addresses from CSV."""
        import pandas as pd
        df = pd.read_csv(df_path)
        return set(df['address'].unique())
    
    def get_missing_contracts(self, addresses: Set[str]) -> List[str]:
        """Identify contracts that don't have ABI files."""
        missing = []
        for address in addresses:
            abi_path = Path(ABI_DIR) / f"{address}.json"
            if not abi_path.exists():
                missing.append(address)
        return missing
    
    def fetch_contract_abi(self, contract_address: str) -> bool:
        """Fetch ABI for a single contract and save to file."""
        if not self.block_explorer:
            logger.warning("No block explorer configured. Cannot fetch ABI.")
            return False
        
        try:
            # Create ABI directory
            os.makedirs(ABI_DIR, exist_ok=True)
            
            # Get contract metadata to check for proxy
            contract_metadata = self.block_explorer.get_contract_metadata(contract_address)
            
            # Fetch main contract ABI
            abi = self.block_explorer.get_contract_abi(contract_address)
            abi_path = Path(ABI_DIR) / f"{contract_address}.json"
            
            with open(abi_path, "w") as f:
                json.dump(json.loads(abi), f, indent=2)
            
            logger.info(f"ABI saved for {contract_address}")
            
            # If it's a proxy, fetch implementation ABI
            if contract_metadata.get("Proxy"):
                implementation_address = contract_metadata.get("Implementation")
                if implementation_address:
                    impl_abi = self.block_explorer.get_contract_abi(implementation_address)
                    impl_path = Path(ABI_DIR) / f"{contract_address}-implementation.json"
                    
                    with open(impl_path, "w") as f:
                        json.dump(json.loads(impl_abi), f, indent=2)
                    
                    logger.info(f"Implementation ABI saved for {contract_address}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to fetch ABI for {contract_address}: {e}")
            return False
    
    def fetch_missing_abis(self, addresses: Set[str], max_workers: int = 3) -> Dict[str, bool]:
        """Fetch ABIs for multiple contracts in parallel."""
        missing = self.get_missing_contracts(addresses)
        
        if not missing:
            logger.info("All contract ABIs are already available.")
            return {}
        
        logger.info(f"Fetching ABIs for {len(missing)} missing contracts...")
        
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_address = {
                executor.submit(self.fetch_contract_abi, addr): addr 
                for addr in missing
            }
            
            for future in as_completed(future_to_address):
                address = future_to_address[future]
                try:
                    success = future.result()
                    results[address] = success
                except Exception as e:
                    logger.error(f"Error fetching ABI for {address}: {e}")
                    results[address] = False
        
        return results
    
    def load_contract_events(self, contract_address: str) -> List[EventDefinition]:
        """Load events for a single contract (including implementation if proxy)."""
        events = []
        
        # Load main contract ABI
        abi_path = Path(ABI_DIR) / f"{contract_address}.json"
        if abi_path.exists():
            with open(abi_path, "r") as f:
                abi = json.load(f)
            events.extend(get_events(abi))
        
        # Load implementation ABI if exists
        impl_path = Path(ABI_DIR) / f"{contract_address}-implementation.json"
        if impl_path.exists():
            with open(impl_path, "r") as f:
                impl_abi = json.load(f)
            events.extend(get_events(impl_abi))
        
        return events
    
    def load_all_events(self, addresses: Set[str]) -> Dict[str, EventDefinition]:
        """Load events from all contract addresses."""
        if not self._events_cache or self._loaded_contracts != addresses:
            logger.info(f"Loading events for {len(addresses)} contracts...")
            
            all_events = []
            for address in addresses:
                events = self.load_contract_events(address)
                all_events.extend(events)
                logger.debug(f"Loaded {len(events)} events for {address}")
            
            # Create lookup by topic0
            self._events_cache = {event["topic0"]: event for event in all_events}
            self._loaded_contracts = addresses.copy()
            
            logger.info(f"Total events loaded: {len(self._events_cache)}")
        
        return self._events_cache
    
    def get_events_by_topic0(self, addresses: Set[str]) -> Dict[str, EventDefinition]:
        """Get all events indexed by topic0 for given addresses."""
        return self.load_all_events(addresses)