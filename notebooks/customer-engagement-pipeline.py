from pyspark.sql import SparkSession, functions as F, Window

spark = (
    SparkSession.builder
    .appName("customer-engagement-platform")
    .master("local[*]")
    .getOrCreate()
)

# Bronze: raw event ingestion
bronze_df = (
    spark.read
    .json("data/sample_events.json")
    .withColumn("ingestion_timestamp", F.current_timestamp())
)

# Silver: clean, standardise, deduplicate
dedupe_window = Window.partitionBy("event_id").orderBy(F.col("ingestion_timestamp").desc())

silver_df = (
    bronze_df
    .withColumn("event_timestamp", F.to_timestamp("event_timestamp"))
    .withColumn("event_date", F.to_date("event_timestamp"))
    .withColumn("order_value", F.coalesce(F.col("order_value"), F.lit(0.0)))
    .withColumn("row_number", F.row_number().over(dedupe_window))
    .filter(F.col("row_number") == 1)
    .drop("row_number")
    .filter(F.col("customer_id").isNotNull())
    .filter(F.col("event_timestamp").isNotNull())
)

# Gold: customer-level engagement metrics
gold_customer_metrics = (
    silver_df
    .groupBy("customer_id")
    .agg(
        F.count("*").alias("total_events"),
        F.sum(F.when(F.col("event_type") == "purchase", 1).otherwise(0)).alias("purchase_count"),
        F.sum("order_value").alias("total_spend"),
        F.max("event_timestamp").alias("last_activity_timestamp"),
        F.countDistinct("campaign_id").alias("campaigns_engaged")
    )
    .withColumn(
        "engagement_score",
        (F.col("total_events") * 5)
        + (F.col("purchase_count") * 20)
        + (F.col("campaigns_engaged") * 10)
    )
    .withColumn(
        "customer_segment",
        F.when(F.col("total_spend") >= 250, "High Value")
         .when(F.col("engagement_score") >= 40, "Highly Engaged")
         .otherwise("Standard")
    )
)

print("Bronze events")
bronze_df.show(truncate=False)

print("Silver events")
silver_df.show(truncate=False)

print("Gold customer metrics")
gold_customer_metrics.show(truncate=False)
