-- PostgreSQL

CREATE TABLE clean_events (
    event_id VARCHAR PRIMARY KEY,
    event_time TIMESTAMP,
    app_id VARCHAR,
    media_source VARCHAR,
    campaign VARCHAR,
    revenue_usd NUMERIC,
    ingested_at TIMESTAMP
);