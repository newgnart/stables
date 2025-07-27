import pandas as pd
import ast

def process_transfer_events(csv_path='decoded_events.csv'):
    """
    Read decoded_events.csv, filter for Transfer events, and transform decoded column to DataFrame.
    
    Args:
        csv_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: DataFrame with Transfer events and expanded decoded columns
    """
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Filter for Transfer events (topic0 = 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef)
    transfer_topic0 = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
    transfer_events = df[df['topic0'] == transfer_topic0].copy()
    
    # Parse the decoded column (which contains dict strings) and expand into separate columns
    decoded_data = []
    for idx, row in transfer_events.iterrows():
        try:
            # Parse the string representation of the dictionary
            decoded_dict = ast.literal_eval(row['decoded'])
            decoded_data.append(decoded_dict)
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing decoded data at row {idx}: {e}")
            decoded_data.append({})
    
    # Create DataFrame from decoded data
    decoded_df = pd.DataFrame(decoded_data)
    
    # Combine original columns with decoded columns
    result_df = pd.concat([
        transfer_events.reset_index(drop=True),
        decoded_df
    ], axis=1)
    
    return result_df

if __name__ == "__main__":
    # Process the transfer events
    result = process_transfer_events()
    
    print(f"Found {len(result)} Transfer events")
    print("\nColumns in the result DataFrame:")
    print(result.columns.tolist())
    print("\nFirst few rows:")
    print(result.head())
    
    # Save to CSV
    result.to_csv('transfer_events_processed.csv', index=False)
    print(f"\nProcessed data saved to 'transfer_events_processed.csv'")