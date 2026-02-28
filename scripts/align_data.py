import pandas as pd
from datetime import datetime, timedelta
import json

def align_tweets_with_news(tweets_csv, news_csv, output_json):
    """
    Aligns tweets with news events within a 24-hour window.
    """
    tweets = pd.read_csv(tweets_csv)
    news = pd.read_csv(news_csv)
    
    # Convert date columns to datetime
    tweets['date'] = pd.to_datetime(tweets['date'])
    news['date'] = pd.to_datetime(news['date'])
    
    aligned_data = []
    
    # Sort for better processing
    tweets = tweets.sort_values('date')
    news = news.sort_values('date')
    
    for _, tweet in tweets.iterrows():
        # Find news on the same day or the day before (24h window)
        tweet_date = tweet['date'].date()
        relevant_news = news[
            (news['date'].dt.date == tweet_date) | 
            (news['date'].dt.date == (tweet_date - timedelta(days=1)))
        ]
        
        if not relevant_news.empty:
            # For MVP, we combine the summaries of relevant days
            combined_news = "\n---\n".join(relevant_news['summary'].tolist())
            
            aligned_data.append({
                "tweet_id": str(tweet.get('tweet_id', '')),
                "tweet_date": tweet['date'].isoformat(),
                "tweet_text": tweet['text'],
                "news_context": combined_news
            })
            
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(aligned_data, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully aligned {len(aligned_data)} tweets with news context.")

if __name__ == "__main__":
    import os
    if not os.path.exists("data"):
        os.makedirs("data")
    
    align_tweets_with_news(
        "data/trump_2018_mvp_tweets.csv", 
        "data/wikipedia_2018_events.csv", 
        "data/aligned_raw_mvp.json"
    )
