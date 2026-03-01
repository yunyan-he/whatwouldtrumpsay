# What Would Trump Say? (WWTS)

**What Would Trump Say?** is an AI-powered prediction engine designed to simulate Donald Trump's potential reactions to current news events based on his historical rhetoric, sentiment patterns, and political targets.

## 🚀 Project Overview
The goal of this project is to build a RAG (Retrieval-Augmented Generation) system that uses historical data (2018-2021) to predict how Trump might respond to contemporary headlines.

## 🛠 Currently Completed: v2 RAG Implementation
We have successfully implemented the **RAG (Retrieval-Augmented Generation) Loop** for the 2018 MVP.

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

### 4. RAG Implementation (v2)
- **Vector Retrieval**: Implemented a FastAPI backend (`main.py`) that queries a **Supabase (pgvector)** store with 1536-dimensional OpenAI embeddings.
- **Time Isolation**: Strict retrieval logic (`WHERE event_date < query_date`) ensures the model only "remembers" the past.
- **Blind Test**: Validated on 50 reserved entries with an automated evaluation scoring **7.0/10** for rhetorical fidelity.

## 📂 Data Directory Map
| File | Category | Status | Purpose |
| :--- | :--- | :--- | :--- |
| `raw_tweets.csv` | Raw | Permanent | Original source. |
| `wikipedia_2018_events.csv` | Raw | Permanent | Scraped news context. |
| `aligned_raw_mvp.json` | Intermediate | **Obsolete** | Replaced by `labeled_mvp_2018.json`. |
| `labeled_mvp_2018.json` | Foundation | **Active** | Labeled "Golden Dataset" (Jan-Sep). |
| `embedded_mvp_2018.json` | Snapshot | **Active** | Vectors currently in Supabase. |
| `test_labeled_2018.json` | Testing | Active | Ground truth for Oct-Dec 2018. |
| `simulation_results_2018.json` | Results | Active | Predictions from the blind test. |

## 🔄 RAG Workflow (v2)
Compared to v1, the v2 workflow adds a full architectural loop:
1. **Narrative Matching**: Classifying events into `strategic_narrative` vs `tactical_response`.
2. **Context Injection**: Top-3 relevant historical events are retrieved and fed into the prompt.
3. **Style Fidelity**: The system prompt ensures the LLM adopts a specific rhetorical persona based on the retrieved context.

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
- **Web UI**: Build a frontend for users to interact with the prediction engine.
- **Full Dataset Expansion**: Scale the pipeline to include 2019-2021 data.
- **Narrative Refinement**: Further tune the "Strategic Narrative" templates to capture long-term rhetorical shifts.

---
*Note: This project is for academic and technical research purposes focusing on NLP and pattern recognition.*
