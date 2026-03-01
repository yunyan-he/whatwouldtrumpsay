import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# We'll use OpenAI's official SDK but point it to OpenRouter or OpenAI directly
# OpenRouter's embedding endpoint is often just standard OpenAI
client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.getenv("LLM_API_KEY")
)

def get_embedding(text, model=os.getenv("LLM_EMBEDDING_MODEL", "openai/text-embedding-3-small")):
    # Embedding dimension depends on the model in .env
    try:
        response = client.embeddings.create(
            input=[text.replace("\n", " ")],
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Error getting embedding: {e}")
        return None

def process_embeddings(input_json, output_json):
    if not os.path.exists(input_json):
        print(f"Error: Input file {input_json} not found.")
        return

    with open(input_json, 'r') as f:
        data = json.load(f)

    print(f"🚀 Starting Embedding Process for {len(data)} entries...")
    
    success_count = 0
    for i, entry in enumerate(data):
        # Combine Event Description and Topic Tags for a richer vector
        tags_str = ", ".join(entry.get("topic_tags", []))
        input_text = f"Event: {entry.get('event_description')}. Topics: {tags_str}"
        
        print(f"[{i+1}/{len(data)}] Embedding: {entry.get('event_description')[:50]}...")
        
        vector = get_embedding(input_text)
        if vector:
            entry["embedding"] = vector
            success_count += 1
        else:
            print(f"  ⚠️ Skipping entry due to error.")
            
        # Rate limiting for free tier if necessary
        time.sleep(0.5)

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"🏁 Finished! Embedded {success_count} entries. Saved to {output_json}")

if __name__ == "__main__":
    process_embeddings("data/labeled_mvp_2018.json", "data/embedded_mvp_2018.json")
