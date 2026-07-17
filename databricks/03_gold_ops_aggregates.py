# Databricks notebook source
from pyspark.sql import functions as F

silver = dbutils.widgets.get("silver_path"); gold = dbutils.widgets.get("gold_path")
events = spark.read.format("delta").load(silver)
latest = events.groupBy("parcel_id").agg(F.max_by(F.struct("event_type", "hub_id", "event_time", "sla_hours"), "event_time").alias("last"))
ops = (latest.select("last.*").groupBy(F.window("event_time", "1 hour"), "hub_id")
 .agg(F.count("*").alias("parcel_count"), F.sum(F.when(~F.col("event_type").isin("DELIVERED", "FAILED_DELIVERY", "RTO_INITIATED"), 1).otherwise(0)).alias("backlog_count")))
ops.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(f"{gold}/ops_hourly")
spark.sql(f"OPTIMIZE delta.`{gold}/ops_hourly` ZORDER BY (hub_id)")
