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
    phase TEXT DEFAULT '2nd Term Prep/2018',
    is_verified BOOLEAN DEFAULT FALSE, -- Manual check flag
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indices for faster lookup
CREATE INDEX idx_raw_tweets_date ON raw_tweets(tweet_date);
CREATE INDEX idx_daily_news_date ON daily_news(event_date);
