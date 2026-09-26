-- PostgreSQL

WITH daily_aggregated AS (
    SELECT
        app_id,
        DATE(event_time) AS event_date,
        COALESCE(SUM(CAST(NULLIF(NULLIF(REPLACE(revenue_usd, ',', '.'), 'NULL'), '') AS NUMERIC)), 0) AS daily_revenue
    FROM vw_clean_events
    GROUP BY app_id, DATE(event_time)
)

SELECT
    app_id,
    event_date,
    daily_revenue,

    -- 1. Загальний дохід від запуску до сьогодні
    SUM(daily_revenue) OVER (
        PARTITION BY app_id
        ORDER BY event_date
    ) AS running_total,

    -- 2. Середній дохід за останній тиждень
    AVG(daily_revenue) OVER (
        PARTITION BY app_id
        ORDER BY event_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d,

    -- 3. Відсоткова зміна доходу між вчора і сьогодні || (Сьогодні - Вчора) / Вчора * 100
    (daily_revenue - LAG(daily_revenue) OVER (PARTITION BY app_id ORDER BY event_date))
    / NULLIF(LAG(daily_revenue) OVER (PARTITION BY app_id ORDER BY event_date), 0) * 100.0 AS dod_change_pct

FROM daily_aggregated
ORDER BY app_id, event_date;