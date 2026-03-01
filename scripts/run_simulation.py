import json
import requests
import os
import time

API_URL = "http://localhost:8000/predict"
INPUT_FILE = "data/test_labeled_2018.json"
OUTPUT_FILE = "data/simulation_results_2018.json"

def run_simulation():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. wait for labeling to finish.")
        return

    with open(INPUT_FILE, 'r') as f:
        test_data = json.load(f)

    results = []
    print(f"🚀 Starting RAG Simulation ({len(test_data)} entries)")
    
    for i, entry in enumerate(test_data):
        print(f"[{i+1}/{len(test_data)}] Simulating: {entry.get('event_description')[:50]}...")
        
        payload = {
            "event_text": entry.get("event_description"),
            "event_date": entry.get("tweet_date").split("T")[0] # Extract the date
        }
        
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                prediction = response.json()
                entry["predicted_tweet"] = prediction["predicted_tweet"]
                entry["context_used"] = prediction["context"]
                results.append(entry)
            else:
                print(f"  ❌ Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            
        # Incremental save
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        time.sleep(1)

    print(f"🏁 Simulation complete! Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_simulation()
