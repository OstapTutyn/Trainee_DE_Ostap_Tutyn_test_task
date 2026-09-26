-- PostgreSQL

CREATE OR REPLACE VIEW task_2_3_join AS
WITH daily_revenue AS (
    SELECT
        DATE(event_time) AS event_date,
        app_id,
        media_source,
        campaign,
        COALESCE(SUM(CAST(NULLIF(NULLIF(REPLACE(revenue_usd, ',', '.'), 'NULL'), '') AS NUMERIC)), 0) AS total_revenue
    FROM vw_clean_events
    GROUP BY DATE(event_time), app_id, media_source, campaign
),
daily_cost AS (
    SELECT
        DATE(date) AS event_date,
        app_id,
        media_source,
        campaign,
        COALESCE(SUM(CAST(cost_usd AS NUMERIC)), 0) AS total_cost
    FROM campaign_costs
    GROUP BY DATE(date), app_id, media_source, campaign
)
SELECT
    COALESCE(r.event_date, c.event_date) AS event_date,
    COALESCE(r.app_id, c.app_id) AS app_id,
    COALESCE(r.media_source, c.media_source) AS media_source,
    COALESCE(r.campaign, c.campaign) AS campaign,
    COALESCE(r.total_revenue, 0) AS revenue,
    COALESCE(c.total_cost, 0) AS cost,

    COALESCE(r.total_revenue, 0) / NULLIF(COALESCE(c.total_cost, 0), 0) AS roas

FROM daily_revenue r
FULL OUTER JOIN daily_cost c
    ON r.event_date = c.event_date
    AND r.app_id = c.app_id
    AND r.media_source = c.media_source
    AND r.campaign = c.campaign
ORDER BY event_date, app_id, media_source, campaign;