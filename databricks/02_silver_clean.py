# Databricks notebook source
from pyspark.sql import functions as F
from pyspark.sql.window import Window

bronze = dbutils.widgets.get("bronze_path"); silver = dbutils.widgets.get("silver_path")
raw = spark.read.format("delta").load(bronze)
w_scan = Window.partitionBy("scan_id").orderBy(F.col("ingest_time").desc())
w_event = Window.partitionBy("parcel_id").orderBy("event_time", "scan_id")
clean = (raw.withColumn("_latest", F.row_number().over(w_scan)).where("_latest = 1")
 .withColumn("event_order", F.row_number().over(w_event))
 .withColumn("phone_hash", F.sha2("phone_number", 256)).drop("phone_number", "_latest")
 .withColumn("is_late", F.col("ingest_time").cast("timestamp") > F.expr("event_time + INTERVAL 6 HOURS")))
clean.createOrReplaceTempView("incoming_silver")
spark.sql(f"""MERGE INTO delta.`{silver}` target USING incoming_silver source ON target.scan_id = source.scan_id
WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *""")
