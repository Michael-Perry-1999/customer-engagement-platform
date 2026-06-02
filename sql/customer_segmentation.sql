-- Customer segmentation model
-- Intended to run against the curated Gold customer metrics layer in Snowflake.

WITH customer_metrics AS (
    SELECT
        customer_id,
        total_events,
        purchase_count,
        total_spend,
        last_activity_timestamp,
        campaigns_engaged,
        engagement_score
    FROM gold.customer_metrics
),

segmented_customers AS (
    SELECT
        customer_id,
        total_events,
        purchase_count,
        total_spend,
        last_activity_timestamp,
        campaigns_engaged,
        engagement_score,

        CASE
            WHEN total_spend >= 250 THEN 'High Value'
            WHEN engagement_score >= 40 THEN 'Highly Engaged'
            WHEN purchase_count = 0 AND total_events >= 2 THEN 'Nurture'
            ELSE 'Standard'
        END AS customer_segment,

        CASE
            WHEN total_spend >= 250 THEN TRUE
            WHEN engagement_score >= 40 THEN TRUE
            ELSE FALSE
        END AS eligible_for_campaign_activation

    FROM customer_metrics
)

SELECT *
FROM segmented_customers;
