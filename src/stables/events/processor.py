"""High-level event processing for dataframes."""

import ast
import logging
from typing import Dict, Any, Optional
import pandas as pd

from .abi_manager import ABIManager
from .decoder import EventDecoder

logger = logging.getLogger(__name__)


class EventProcessor:
    """High-level processor for decoding events in dataframes."""
    
    def __init__(self, api_key: Optional[str] = None, chain_name: str = "mainnet"):
        """Initialize event processor."""
        self.abi_manager = ABIManager(api_key=api_key, chain_name=chain_name)
        self.decoder: Optional[EventDecoder] = None
    
    def process_dataframe(self, df_path: str, fetch_missing: bool = True) -> pd.DataFrame:
        """Process CSV dataframe and add topic0 and decoded columns."""
        logger.info(f"Processing dataframe: {df_path}")
        
        # Load dataframe
        df = pd.read_csv(df_path)
        logger.info(f"Loaded dataframe with shape: {df.shape}")
        
        # Get all contract addresses
        addresses = self.abi_manager.get_all_contract_addresses(df_path)
        logger.info(f"Found {len(addresses)} unique contract addresses")
        
        # Fetch missing ABIs if requested
        if fetch_missing:
            missing = self.abi_manager.get_missing_contracts(addresses)
            if missing:
                logger.info(f"Fetching ABIs for {len(missing)} missing contracts...")
                results = self.abi_manager.fetch_missing_abis(addresses)
                
                # Log results
                successful = sum(1 for success in results.values() if success)
                logger.info(f"Successfully fetched {successful}/{len(missing)} ABIs")
                
                for addr, success in results.items():
                    if not success:
                        logger.warning(f"Failed to fetch ABI for {addr}")
        
        # Load all events
        events_by_topic0 = self.abi_manager.get_events_by_topic0(addresses)
        self.decoder = EventDecoder(events_by_topic0)
        
        # Parse topics column (convert string representation of list to actual list)
        df['topics_parsed'] = df['topics'].apply(
            lambda x: ast.literal_eval(x) if pd.notna(x) else []
        )
        
        # Extract topic0
        df['topic0'] = df['topics_parsed'].apply(
            lambda topics: topics[0] if topics else None
        )
        
        # Decode events
        def decode_row(row) -> Optional[Dict[str, Any]]:
            topics = row['topics_parsed']
            if not isinstance(topics, list) or len(topics) == 0:
                return None
            
            decoded_event = self.decoder.decode_log_entry(
                row['address'], topics, row['data']
            )
            
            # Convert DecodedEvent to dict for DataFrame storage
            result = {
                'event': decoded_event.event_name,
                'is_unknown': decoded_event.is_unknown,
                **decoded_event.parameters
            }
            
            # Add address to the result
            result['address'] = decoded_event.address
            
            # If unknown, include raw data for debugging
            if decoded_event.is_unknown:
                result['raw_topics'] = decoded_event.raw_topics
                result['raw_data'] = decoded_event.raw_data
            
            return result
        
        logger.info("Decoding events...")
        df['decoded'] = df.apply(decode_row, axis=1)
        
        # Drop temporary column
        df = df.drop('topics_parsed', axis=1)
        
        # Log decoding statistics
        total_events = len(df)
        unknown_events = df['decoded'].apply(
            lambda x: x.get('is_unknown', False) if x else True
        ).sum()
        decoded_events = total_events - unknown_events
        
        logger.info(f"Decoding complete:")
        logger.info(f"  Total events: {total_events}")
        logger.info(f"  Successfully decoded: {decoded_events}")
        logger.info(f"  Unknown events: {unknown_events}")
        logger.info(f"  Success rate: {decoded_events/total_events*100:.1f}%")
        
        return df
    
    def get_decoding_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get statistics about decoded events."""
        if 'decoded' not in df.columns:
            return {}
        
        total = len(df)
        unknown = df['decoded'].apply(
            lambda x: x.get('is_unknown', False) if x else True
        ).sum()
        
        # Get event type counts
        event_counts = {}
        for _, row in df.iterrows():
            decoded = row.get('decoded')
            if decoded and not decoded.get('is_unknown', False):
                event_name = decoded.get('event', 'unknown')
                event_counts[event_name] = event_counts.get(event_name, 0) + 1
        
        return {
            'total_events': total,
            'decoded_events': total - unknown,
            'unknown_events': unknown,
            'success_rate': (total - unknown) / total * 100 if total > 0 else 0,
            'event_type_counts': event_counts
        }