import os
import json
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI

load_dotenv()

app = FastAPI(title="What Would Trump Say API (v2)")

# Initialize Clients
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
llm_client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.getenv("LLM_API_KEY")
)

class QueryRequest(BaseModel):
    event_text: str
    event_date: str  # Format: YYYY-MM-DD

class PredictionResponse(BaseModel):
    predicted_tweet: str
    context: List[dict]

SYSTEM_PROMPT = """
You are Donald J. Trump, the 45th President of the United States. 
You are known for your unique rhetorical style: direct, punchy, frequent use of superlatives (Great, Terrible, Fake), 
and clear distinction between "winners" and "losers".

Your task is to respond to a new news event based on your historical patterns. 
I will provide you with 3 similar historical contexts (events and your actual responses to them). 
Use these to inform the tone, target, and narrative strategy of your new response.

RULES:
1. Stay in character as Donald J. Trump.
2. Keep it under 280 characters.
3. Use his signature vocabulary and punctuation (e.g., "MAGA!", "Fake News!", "Witch Hunt!").
4. If the context shows a specific recurring target (like Democrats or the Media), maintain that stance.

Reference Contexts:
{context_str}

New Event to respond to:
{new_event}

Predict your tweet response:
"""

def get_embedding(text: str):
    try:
        response = llm_client.embeddings.create(
            input=[text.replace("\n", " ")],
            model=os.getenv("LLM_EMBEDDING_MODEL", "openai/text-embedding-3-small")
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

@app.post("/predict", response_model=PredictionResponse)
async def predict_trump_response(request: QueryRequest):
    # 1. Generate Embedding for the new event
    query_vector = get_embedding(request.event_text)
    if not query_vector:
        raise HTTPException(status_code=500, detail="Failed to generate embedding")

    # 2. Query Supabase for Top-3 similar events with Time Isolation
    try:
        # RPC match_events(query_embedding, match_threshold, match_count, query_date)
        rpc_params = {
            "query_embedding": query_vector,
            "match_threshold": 0.3,
            "match_count": 3,
            "query_date": request.event_date
        }
        res = supabase.rpc("match_events", rpc_params).execute()
        
        contexts = res.data if res.data else []
    except Exception as e:
        print(f"Supabase RPC error: {e}")
        raise HTTPException(status_code=500, detail=f"Database retrieval failed: {str(e)}")

    # 3. Format context for the Prompt
    context_str = ""
    for i, c in enumerate(contexts):
        context_str += f"Context {i+1}:\n"
        context_str += f"- Historical Event: {c['event_description']}\n"
        context_str += f"- Actual Response: {c['actual_response']}\n\n"

    # 4. Generate Response using LLM
    try:
        full_prompt = SYSTEM_PROMPT.format(
            context_str=context_str if context_str else "No direct historical match found.",
            new_event=request.event_text
        )
        
        predicted_tweet = completion.choices[0].message.content.strip()
        
        # Strip potential quotes if the model wrapped the response
        if predicted_tweet.startswith('"') and predicted_tweet.endswith('"'):
            predicted_tweet = predicted_tweet[1:-1]
            
        return PredictionResponse(
            predicted_tweet=predicted_tweet,
            context=contexts
        )
    except Exception as e:
        print(f"LLM Generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
