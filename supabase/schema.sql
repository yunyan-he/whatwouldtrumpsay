-- Enable pgvector extension for future RAG phase
CREATE EXTENSION IF NOT EXISTS vector;

-- Table for raw tweets (2018 focus)
CREATE TABLE IF NOT EXISTS raw_tweets (
    id BIGSERIAL PRIMARY KEY,
    external_id TEXT UNIQUE, -- Original tweet ID
    tweet_date TIMESTAMP WITH TIME ZONE NOT NULL,
    content TEXT NOT NULL,
    retweet_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    is_deleted BOOLEAN DEFAULT FALSE,
    device TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for daily news from Wikipedia
CREATE TABLE IF NOT EXISTS daily_news (
    id SERIAL PRIMARY KEY,
    event_date DATE UNIQUE NOT NULL,
    summary TEXT NOT NULL, -- Full scraped content for that day
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for the "Aligned & Labeled" dataset (The Golden Dataset)
CREATE TABLE IF NOT EXISTS trumpsay_mvp_2018 (
    id SERIAL PRIMARY KEY,
    original_tweet_id BIGINT REFERENCES raw_tweets(id),
    news_id INTEGER REFERENCES daily_news(id),
    event_description TEXT NOT NULL, -- LLM-extracted concise event
    topic_tags TEXT[], -- e.g., ['Trade War', 'China', 'Midterms']
    sentiment TEXT, -- attack/support/deflect
    target TEXT, -- who or what is he responding to
    target_type TEXT, -- individual, institution/media, group/abstract
    trigger_type TEXT, -- tactical_response, strategic_narrative, personal_noise
    predicted_response TEXT, -- Reserved for testing phase
    actual_response TEXT, -- Copy of original tweet text for convenience
    embedding vector(1536), -- For RAG retrieval (e.g., text-embedding-3-small)
    phase TEXT DEFAULT '2nd Term Prep/2018',
    is_verified BOOLEAN DEFAULT FALSE, -- Manual check flag
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Function for cosine similarity search
-- Note: we use <=> for cosine distance, so 1 - (A <=> B) is cosine similarity
CREATE OR REPLACE FUNCTION match_events (
  query_embedding vector(1536),
  match_threshold float,
  match_count int,
  query_date date
)
RETURNS TABLE (
  id int,
  event_description text,
  actual_response text,
  topic_tags text[],
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    trumpsay_mvp_2018.id,
    trumpsay_mvp_2018.event_description,
    trumpsay_mvp_2018.actual_response,
    trumpsay_mvp_2018.topic_tags,
    1 - (trumpsay_mvp_2018.embedding <=> query_embedding) AS similarity
  FROM trumpsay_mvp_2018
  JOIN daily_news ON trumpsay_mvp_2018.news_id = daily_news.id
  WHERE daily_news.event_date < query_date
    AND 1 - (trumpsay_mvp_2018.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;

-- Indices for faster lookup
CREATE INDEX idx_raw_tweets_date ON raw_tweets(tweet_date);
CREATE INDEX idx_daily_news_date ON daily_news(event_date);
