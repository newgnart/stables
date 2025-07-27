"""Example usage of the modular event decoding system."""

import os
from stables.events import EventProcessor

def main():
    """Example of how to use the event processing system."""
    
    # Initialize with API key for automatic ABI fetching
    api_key = os.getenv("ETHERSCAN_API_KEY")
    processor = EventProcessor(api_key=api_key, chain_name="mainnet")
    
    # Process a CSV file with event logs
    csv_path = "notebooks/e.csv"
    
    # This will automatically:
    # 1. Load the CSV
    # 2. Extract unique contract addresses
    # 3. Fetch missing ABIs (including proxy implementations)
    # 4. Load all events from ABIs
    # 5. Decode all events in the dataframe
    # 6. Add 'topic0' and 'decoded' columns
    df = processor.process_dataframe(csv_path, fetch_missing=True)
    
    # Get statistics
    stats = processor.get_decoding_stats(df)
    print(f"Success rate: {stats['success_rate']:.1f}%")
    
    # Save results
    df.to_csv("decoded_events.csv", index=False)
    
    return df

if __name__ == "__main__":
    main()