import json
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
MODEL = os.getenv("LLM_MODEL") # Explicitly use .env model

def label_entry(news_context, tweet_text):
    prompt = f"""
You are an expert political analyst specializing in Donald Trump's rhetoric and behavior.
Given the following news context and his subsequent tweet, identify:
1. The trigger type. Choose exactly one:
   - "tactical_response": Direct response to a specific news event from the last 24h.
   - "strategic_narrative": Activating a long-term narrative/rhetorical template (e.g., "Witch Hunt", "Fake News") regardless of specific new developments.
   - "personal_noise": Personal greetings, holiday wishes, or non-political content.
2. The specific event or narrative description. 
   - If tactical: Describe the triggering event (concise, neutral).
   - If strategic: Describe the recurring narrative context.
3. The topic tags.
4. The target.

News Context:
{news_context}

Trump's Tweet:
{tweet_text}

Output in STRICT JSON format:
{{
  "trigger_type": "...",
  "event_description": "...",
  "topic_tags": ["..."],
  "target": "..."
}}
"""
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/aerin/whatwouldtrumpsay",
        "X-Title": "What Would Trump Say Evaluation",
    }
    
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        res_json = response.json()
        content = res_json['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        print(f"Error: {e}")
        return None

def process_test_labeling(input_json, output_json, start=175, end=200):
    # Load existing labels if any
    if os.path.exists(output_json):
        with open(output_json, 'r') as f:
            labeled_test = json.load(f)
    else:
        labeled_test = []

    with open(input_json, 'r') as f:
        data = json.load(f)
        
    test_set = data[start:end]
    
    print(f"🚀 Labeling Test Set ({len(test_set)} entries: {start}-{end})")
    
    for i, entry in enumerate(test_set):
        print(f"[{i+1}/{len(test_set)}] Labeling: {entry['tweet_text'][:50]}...")
        result = label_entry(entry['news_context'], entry['tweet_text'])
        if result:
            entry.update(result)
            labeled_test.append(entry)
        
        # Save every step for safety
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(labeled_test, f, ensure_ascii=False, indent=2)
            
        time.sleep(1)

    print(f"🏁 Done! Saved to {output_json}")

if __name__ == "__main__":
    process_test_labeling("data/aligned_raw_mvp.json", "data/test_labeled_2018.json")
