import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

def upload_data(json_file):
    if not URL or not KEY:
        print("Missing Supabase URL or Key in .env")
        return

    supabase: Client = create_client(URL, KEY)
    
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Note: Adjust mapping to match schema.sql exactly
    # Since we are using trumpsay_mvp_2018 table
    for entry in data:
        # 1. Insert/Update Daily News first (optional if already exists)
        # 2. Insert/Update Raw Tweet
        # 3. Insert into MVP table
        
        # Simplified for MVP: Direct insert into a combined table if needed, 
        # or follow the relational schema.
        
        # For now, let's assume we use a flat table for the MVP RAG testing
        # Or a simplified version of trumpsay_mvp_2018
        
        payload = {
            "event_description": entry.get("event_description"),
            "topic_tags": entry.get("topic_tags"),
            "sentiment": entry.get("sentiment"),
            "target": entry.get("target"),
            "target_type": entry.get("target_type"),
            "actual_response": entry.get("tweet_text"),
            "phase": "2018_MVP"
        }
        
        try:
            # Check if this tweet text already exists to prevent duplicates
            existing = supabase.table("trumpsay_mvp_2018").select("id").eq("actual_response", entry.get("tweet_text")).execute()
            
            if existing.data:
                # Update existing record
                supabase.table("trumpsay_mvp_2018").update(payload).eq("actual_response", entry.get("tweet_text")).execute()
                print(f"🔄 Updated existing record: {entry.get('tweet_text')[:40]}...")
            else:
                # Insert new record
                supabase.table("trumpsay_mvp_2018").insert(payload).execute()
                print(f"✅ Uploaded new record: {entry.get('tweet_text')[:40]}...")
                
        except Exception as e:
            print(f"❌ Error processing record: {e}")

if __name__ == "__main__":
    upload_data("data/labeled_mvp_2018.json")
