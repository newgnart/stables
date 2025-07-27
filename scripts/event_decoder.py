"""Event decoding script using the modular event processing system."""

import os
import logging
from stables.utils.logging import setup_logging
from stables.events.processor import EventProcessor

logger = logging.getLogger(__name__)
setup_logging()


def main():
    """Main function to process events with the new modular system."""
    # Initialize processor with API key from environment
    api_key = os.getenv("ETHERSCAN_API_KEY")
    if not api_key:
        logger.warning("ETHERSCAN_API_KEY not found. ABI fetching will be disabled.")
    
    processor = EventProcessor(api_key=api_key, chain_name="mainnet")
    
    # Process the CSV file
    csv_path = "notebooks/e.csv"
    logger.info("=== Processing Events with Modular System ===")
    
    try:
        # Process dataframe with automatic ABI fetching
        df = processor.process_dataframe(csv_path, fetch_missing=True)
        
        # Get decoding statistics
        stats = processor.get_decoding_stats(df)
        
        logger.info("=== Decoding Statistics ===")
        logger.info(f"Total events: {stats['total_events']}")
        logger.info(f"Successfully decoded: {stats['decoded_events']}")
        logger.info(f"Unknown events: {stats['unknown_events']}")
        logger.info(f"Success rate: {stats['success_rate']:.1f}%")
        
        if stats['event_type_counts']:
            logger.info("Event type distribution:")
            for event_type, count in sorted(stats['event_type_counts'].items()):
                logger.info(f"  {event_type}: {count}")
        
        # Save results
        output_path = "decoded_events.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"Results saved to {output_path}")
        
        # Show sample decoded events
        logger.info("=== Sample Decoded Events ===")
        for idx, row in df.head(5).iterrows():
            decoded = row.get('decoded', {})
            logger.info(f"Row {idx}:")
            logger.info(f"  Address: {row['address']}")
            logger.info(f"  Topic0: {row.get('topic0', 'N/A')}")
            logger.info(f"  Event: {decoded.get('event', 'unknown')}")
            logger.info(f"  Is Unknown: {decoded.get('is_unknown', True)}")
            if not decoded.get('is_unknown', True):
                # Show decoded parameters (excluding metadata)
                params = {k: v for k, v in decoded.items() 
                         if k not in ['event', 'is_unknown', 'address', 'raw_topics', 'raw_data']}
                if params:
                    logger.info(f"  Parameters: {params}")
            logger.info("---")
        
        return df
        
    except Exception as e:
        logger.error(f"Error processing events: {e}")
        raise


if __name__ == "__main__":
    main()