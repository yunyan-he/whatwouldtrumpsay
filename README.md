# What Would Trump Say? (WWTS)

**What Would Trump Say?** is an AI-powered prediction engine designed to simulate Donald Trump's potential reactions to current news events based on his historical rhetoric, sentiment patterns, and political targets.

## 🚀 Project Overview
The goal of this project is to build a RAG (Retrieval-Augmented Generation) system that uses historical data (2018-2021) to predict how Trump might respond to contemporary headlines.

## 🛠 Currently Completed: MVP Phase 1 (Data Pipeline)
We have successfully completed the foundation of the project: the **Automated Data Pipeline for 2018 MVP**.

### 1. Data Acquisition
- **Twitter Archive**: Processed historical tweets from 2018, filtering for high-engagement, original responses (excluding retweets).
- **Global Events**: Scraped historical news data from Wikipedia to provide context for each specific date.

### 2. Data Alignment
- Each tweet is automatically matched with a 24-hour window of global news events using `scripts/align_data.py`. This creates a dataset where the "Event" and the "Response" are linked with context.

### 3. AI Labeling & Analysis
- Developed a labeling agent using **OpenRouter (Qwen/DeepSeek)** to analyze the raw data.
- The agent extracts 6 key dimensions for **Narrative Alignment**:
    - **Trigger Type**: Classified as `tactical_response` (event-driven), `strategic_narrative` (template-driven), or `personal_noise`.
    - **Event/Narrative Description**: Either a same-day headline (tactical) or a recurring narrative context (strategic).
    - **Topic Tags**: Narrative framework identifiers (e.g., "Witch Hunt", "Border Crisis").
    - **Sentiment**: Attack, Support, or Deflect (**Relative to the target**).
    - **Target**: The specific entity or group mentioned.
    - **Target Type**: Categorized as `individual`, `institution/media`, or `group/abstract`.

### 4. Cloud Infrastructure
- **Database**: Initialized a **Supabase Cloud (PostgreSQL)** instance with the `pgvector` extension for future RAG capabilities.
- **Synchronization**: Implemented an idempotent upload script (`scripts/upload_to_supabase.py`) that handles deduplication and data updates seamlessly.

## 📂 Project Structure
```bash
.
├── scripts/
│   ├── process_tweets.py      # Filters raw CSV tweet data
│   ├── acquire_news.py        # Scrapes data from Wikipedia
│   ├── align_data.py          # Matches tweets with news context
│   ├── labeling_agent.py      # AI analysis via OpenRouter
│   └── upload_to_supabase.py  # Cloud synchronization
├── supabase/
│   └── schema.sql             # Database schema definitions
├── docs/
│   └── project_overview.md    # Detailed 6-point roadmap
└── data/                      # (Git ignored) Local raw/processed data
```

## 📈 Next Steps
- **RAG Implementation**: Build the backend using **FastAPI** to query the Supabase vector store.
- **Prompt Engineering**: Refine the prediction model to match Trump's unique voice and tone.
- **Full Dataset Expansion**: Scale the pipeline to include 2018-2021 data.

---
*Note: This project is for academic and technical research purposes focusing on NLP and pattern recognition.*
