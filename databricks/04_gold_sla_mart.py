# Databricks notebook source
from pyspark.sql import functions as F

silver = dbutils.widgets.get("silver_path"); gold = dbutils.widgets.get("gold_path")
e = spark.read.format("delta").load(silver)
facts = (e.groupBy("parcel_id").agg(F.min("event_time").alias("pickup_time"), F.max_by(F.struct("event_type", "event_time", "lane_id", "sla_hours", "origin_hub", "destination_hub"), "event_time").alias("last"))
 .select("parcel_id", "pickup_time", "last.*").withColumn("actual_hours", (F.unix_timestamp("event_time") - F.unix_timestamp("pickup_time")) / 3600)
 .withColumn("breach_flag", F.col("actual_hours") > F.col("sla_hours")))
facts.write.format("delta").mode("overwrite").save(f"{gold}/fct_sla")
# Time travel example: spark.read.format("delta").option("versionAsOf", 0).load(f"{gold}/fct_sla")
