-- Dialect: PostgreSQL

CREATE OR REPLACE VIEW vw_clean_events AS
WITH ranked_events AS (
    SELECT
        event_id,
        user_id,
        app_id,
        event_name,
        event_time,
        ingested_at,
        country,
        media_source,
        campaign,
        revenue_usd,
        ROW_NUMBER() OVER (
            PARTITION BY event_id
            ORDER BY ingested_at DESC, event_time DESC
        ) as rn
    FROM events_raw
    WHERE is_test = FALSE
)
SELECT
    event_id,
    user_id,
    app_id,
    event_name,
    event_time,
    ingested_at,
    country,
    media_source,
    campaign,
    revenue_usd
FROM ranked_events
WHERE rn = 1;