# Design Decisions

## Why medallion architecture?

The platform separates data into Bronze, Silver and Gold layers to make the pipeline easier to govern, debug and scale.

- Bronze preserves raw source data for audit and replay.
- Silver applies standardisation, deduplication and quality checks.
- Gold provides business-ready datasets for analytics and activation.

## Why PySpark / Databricks?

PySpark is suitable for processing large volumes of customer event data, especially where workloads may grow from batch ingestion into near real-time or streaming patterns.

In a production Databricks implementation, this could be extended using Delta Lake, Auto Loader, Databricks Workflows and Delta Live Tables.

## Why Snowflake?

Snowflake is used as the serving layer for analytics and marketing segmentation workloads.

This allows curated datasets to be exposed to BI tools, marketing teams and activation platforms without coupling them directly to the transformation layer.

## Idempotency

Customer event platforms often receive duplicate or replayed events from upstream systems. The pipeline deduplicates by `event_id` to support consistent outputs when data is reprocessed.

## Data quality

Records are standardised before promotion into curated layers. In production, invalid records would typically be quarantined for investigation rather than silently discarded.

## Governance

Customer data may contain PII, so a production implementation would include role-based access control, masking policies, column-level security and clear ownership of customer identifiers.

## Scaling considerations

For larger datasets, the platform would need:

- partitioning by event date
- incremental processing
- schema evolution handling
- orchestration
- observability and alerting
- cost controls across both Spark and Snowflake compute
