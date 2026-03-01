import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

def upload_data(json_file):
    if not URL or not KEY:
        print("Missing Supabase URL or Key in .env")
        return

    supabase: Client = create_client(URL, KEY)
    
    if not os.path.exists(json_file):
        print(f"File {json_file} does not exist. Skipping upload.")
        return

    with open(json_file, 'r') as f:
        data = json.load(f)

    print(f"🚀 Starting RAG Data Upload ({len(data)} entries)...")
    
    for entry in data:
        # 1. Handle Daily News
        # Extract date from tweet_date (YYYY-MM-DD)
        full_date = entry.get("tweet_date")
        if not full_date:
            print(f"⚠️ Missing date for entry, skipping.")
            continue
            
        event_date = full_date.split("T")[0]
        
        try:
            # Check if news already exists for this date
            news_res = supabase.table("daily_news").select("id").eq("event_date", event_date).execute()
            
            if news_res.data:
                news_id = news_res.data[0]["id"]
            else:
                # Insert news context
                news_payload = {
                    "event_date": event_date,
                    "summary": entry.get("news_context", "No context provided")
                }
                insert_news = supabase.table("daily_news").insert(news_payload).execute()
                news_id = insert_news.data[0]["id"]
                print(f"📰 Created news entry for {event_date}")
                
            # 2. Handle MVP Entry
            payload = {
                "news_id": news_id,
                "event_description": entry.get("event_description"),
                "topic_tags": entry.get("topic_tags"),
                "sentiment": entry.get("sentiment"),
                "target": entry.get("target"),
                "target_type": entry.get("target_type"),
                "trigger_type": entry.get("trigger_type"),
                "actual_response": entry.get("tweet_text"),
                "embedding": entry.get("embedding"), # This might be None if not yet embedded
                "phase": "2018_MVP_RAG"
            }
            
            # Use actual_response (tweet text) as a unique identifier for deduplication
            existing = supabase.table("trumpsay_mvp_2018").select("id").eq("actual_response", entry.get("tweet_text")).execute()
            
            if existing.data:
                # Update
                supabase.table("trumpsay_mvp_2018").update(payload).eq("id", existing.data[0]["id"]).execute()
                print(f"🔄 Updated entry: {entry.get('tweet_text')[:40]}...")
            else:
                # Insert
                supabase.table("trumpsay_mvp_2018").insert(payload).execute()
                print(f"✅ Inserted entry: {entry.get('tweet_text')[:40]}...")
                
        except Exception as e:
            print(f"❌ Error processing record for {event_date}: {e}")

if __name__ == "__main__":
    # Choose the most advanced version of the data available
    if os.path.exists("data/embedded_mvp_2018.json"):
        upload_data("data/embedded_mvp_2018.json")
    elif os.path.exists("data/labeled_mvp_2018.json"):
        upload_data("data/labeled_mvp_2018.json")
    else:
        print("No processed data found in data/ folder.")
