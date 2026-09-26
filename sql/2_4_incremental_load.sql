-- PostgreSQL

INSERT INTO clean_events (event_id, event_time, app_id, media_source, campaign, revenue_usd, ingested_at)
SELECT
    event_id,
    CAST(event_time AS TIMESTAMP),
    app_id,
    media_source,
    campaign,
    COALESCE(CAST(NULLIF(NULLIF(REPLACE(revenue_usd, ',', '.'), 'NULL'), '') AS NUMERIC), 0),
    CAST(ingested_at AS TIMESTAMP)
FROM events_raw
WHERE CAST(ingested_at AS TIMESTAMP) >= CURRENT_DATE - INTERVAL '3 days'

ON CONFLICT (event_id)
DO UPDATE SET
    event_time = EXCLUDED.event_time,
    app_id = EXCLUDED.app_id,
    media_source = EXCLUDED.media_source,
    campaign = EXCLUDED.campaign,
    revenue_usd = EXCLUDED.revenue_usd,
    ingested_at = EXCLUDED.ingested_at;