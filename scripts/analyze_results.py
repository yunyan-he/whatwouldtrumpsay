import json
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
MODEL = os.getenv("LLM_MODEL")
BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")

def judge_accuracy(actual, predicted, context):
    prompt = f"""
You are an expert critic of political communication. Rate the following "Trump-style" AI prediction compared to his actual historical tweet.

Historical Context Provided to AI:
{context}

Actual Historical Tweet:
{actual}

AI Predicted Tweet:
{predicted}

Rate the prediction on a scale of 1-10 for:
1. Rhetorical Fidelity (Vocabulary, Punctuation, Tone): /10
2. Narrative Alignment (Does it pick the right "enemy" or "victory"?): /10
3. Concise Reasoning (1 sentence): 

Output STRICT JSON:
{{
  "rhetorical_score": 0,
  "narrative_score": 0,
  "reasoning": "..."
}}
"""
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(BASE_URL + "/chat/completions", headers=headers, json=payload)
        return json.loads(res.json()['choices'][0]['message']['content'])
    except:
        return None

def analyze():
    with open('data/simulation_results_2018.json', 'r') as f:
        results = json.load(f)
    
    analysis = []
    print(f"🧐 Analyzing {len(results)} results...")
    
    for i, entry in enumerate(results[:10]): # Analyze first 10 for sample
        print(f"[{i+1}/10] Judging...")
        context_summary = "\n".join([f"- {c['event_description']}" for c in entry.get('context_used', [])])
        score = judge_accuracy(entry['tweet_text'], entry['predicted_tweet'], context_summary)
        if score:
            entry['eval'] = score
            analysis.append(entry)
        time.sleep(1)

    # Calculate final stats
    avg_rh = sum(e['eval']['rhetorical_score'] for e in analysis) / len(analysis)
    avg_na = sum(e['eval']['narrative_score'] for e in analysis) / len(analysis)
    
    report = {
        "total_evaluated": len(analysis),
        "avg_rhetorical_fidelity": avg_rh,
        "avg_narrative_alignment": avg_na,
        "samples": analysis
    }
    
    with open('data/evaluation_report_2018.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Report generated: data/evaluation_report_2018.json")
    print(f"Average Rhetorical Score: {avg_rh}/10")

if __name__ == "__main__":
    analyze()
