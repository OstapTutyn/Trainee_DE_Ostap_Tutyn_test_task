1. Оскільки тестові CSV-файли не були прикріплені до завдання, я згенерував еквівалентний набір 
mock-даних самостійно, як це передбачено в секції 1

2. Завдання 2_3: створив clean_table
-- PostgreSQL

CREATE TABLE clean_events (
    event_id VARCHAR PRIMARY KEY, -- Унікальний ідентифікатор події (обов'язково для ON CONFLICT)
    event_time TIMESTAMP,
    app_id VARCHAR,
    media_source VARCHAR,
    campaign VARCHAR,
    revenue_usd NUMERIC,
    ingested_at TIMESTAMP
);
За staging_table візьму events_raw.csv