import pandas as pd

def process_2018_tweets(input_csv, output_csv):
    """
    Filters the raw Trump In Office tweets for the year 2018.
    """
    # Use skipinitialspace and quotechar to be safe
    # Based on 'head' output: ID, Time, Tweet URL, Tweet Text
    try:
        df = pd.read_csv(
            input_csv, 
            skipinitialspace=True, 
            quoting=0, # csv.QUOTE_MINIMAL
            on_bad_lines='skip',
            encoding='utf-8'
        )
    except Exception as e:
        print(f"Initial read failed: {e}. Trying with different settings...")
        df = pd.read_csv(input_csv, on_bad_lines='skip', encoding='latin1')

    # Map actual columns to what we want
    # Actual: 'ID', 'Time', 'Tweet URL', 'Tweet Text'
    # We want: 'id', 'date', 'text'
    
    if 'Time' in df.columns:
        df['date_dt'] = pd.to_datetime(df['Time'], errors='coerce')
    else:
        # Try finding the time column by index if names are messy
        df['date_dt'] = pd.to_datetime(df.iloc[:, 1], errors='coerce')
        df.columns = ['ID', 'Time', 'Tweet URL', 'Tweet Text']
        
    # Drop rows with invalid dates
    df = df.dropna(subset=['date_dt'])
    
    # Filter for 2018
    df_2018 = df[df['date_dt'].dt.year == 2018]
    
    # Filter for original tweets
    # Text is usually the 4th column
    tweet_col = 'Tweet Text' if 'Tweet Text' in df.columns else df.columns[3]
    df_2018 = df_2018[~df_2018[tweet_col].str.startswith('RT @', na=False)]
    
    # Sort and take top ones by some metric if possible
    # This specific CSV doesn't seem to have engagement counts in the first few lines?
    # Let's check columns again. 
    print(f"Columns found: {df.columns.tolist()}")
    
    # If no engagement, just take a good sample of 200
    df_mvp = df_2018.sample(min(200, len(df_2018)), random_state=42).sort_values('date_dt')
    
    # Final cleanup
    df_mvp = df_mvp.rename(columns={
        'ID': 'tweet_id',
        'Tweet Text': 'text',
        'Time': 'date'
    })
    
    df_mvp.to_csv(output_csv, index=False)
    print(f"Processed {len(df_mvp)} representative tweets for 2018 (including IDs).")

if __name__ == "__main__":
    process_2018_tweets("data/raw_tweets.csv", "data/trump_2018_mvp_tweets.csv")
