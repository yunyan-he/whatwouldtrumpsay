import json
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-chat")

def label_entry(news_context, tweet_text):
    prompt = f"""
You are an expert political analyst specializing in Donald Trump's rhetoric and behavior.
Given the following news context and his subsequent tweet, identify:
1. The specific event he is responding to. Describe the triggering event as it would reasonably appear in same-day news headlines, without retrospective interpretation.
2. The topic tags (e.g., "Immigration", "Trade", "Media").
3. The sentiment (attack, support, or deflect). Specific Definition: This must represent Trump's attitude towards the primary TARGET, not the event itself.
4. The target of his statement (e.g., "Democrats", "China", "NYT").
5. The target type. Choose exactly one: "individual", "institution/media", or "group/abstract".

News Context:
{news_context}

Trump's Tweet:
{tweet_text}

Output in STRICT JSON format:
{{
  "event_description": "...",
  "topic_tags": ["...", "..."],
  "sentiment": "...",
  "target": "...",
  "target_type": "..."
}}
"""
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/aerin/whatwouldtrumpsay", # Required for OpenRouter Free
        "X-Title": "What Would Trump Say MVP", # Recommended for OpenRouter
    }
    
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        res_json = response.json()
        if 'choices' not in res_json:
            print(f"API Error Response: {res_json}")
            return None
        content = res_json['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        print(f"Error labeling entry: {e}")
        return None

def process_labeling(input_json, output_json, limit=20):
    if not os.path.exists(input_json):
        print(f"Error: Input file {input_json} not found.")
        return

    with open(input_json, 'r') as f:
        data = json.load(f)
        
    labeled_data = []
    to_process = data[:limit]
    
    print(f"\n🚀 Starting Labeling Process ({len(to_process)} entries)")
    print(f"Using Model: {MODEL}")
    print("-" * 50)
    
    success_count = 0
    for i, entry in enumerate(to_process):
        tweet_preview = entry['tweet_text'][:60].replace('\n', ' ') + "..."
        print(f"[{i+1}/{len(to_process)}] Processing Tweet: {tweet_preview}")
        
        result = label_entry(entry['news_context'], entry['tweet_text'])
        
        if result:
            entry.update(result)
            labeled_data.append(entry)
            success_count += 1
            print(f"  ✅ Success: {result.get('event_description', 'No event desc')[:50]}...")
            print(f"     Tags: {result.get('topic_tags')} | Target: {result.get('target')}")
        else:
            print(f"  ❌ Failed to label this entry.")
            
        if i < len(to_process) - 1:
            time.sleep(1) # Gentle rate limiting for free models
        
    print("-" * 50)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(labeled_data, f, ensure_ascii=False, indent=2)
    
    print(f"🏁 Finished! Saved {success_count} labeled entries to {output_json}")
    print(f"Check the file to verify quality.")

if __name__ == "__main__":
    if not LLM_API_KEY:
        print("❌ Error: Please set LLM_API_KEY in .env")
    else:
        # Increase limit or adjust as needed
        process_labeling("data/aligned_raw_mvp.json", "data/labeled_mvp_2018.json", limit=20)
