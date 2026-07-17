# Databricks notebook source
# COMMAND ----------
# Read raw JSON without rejecting forward-compatible fields; persist malformed values in _rescued_data.
from pyspark.sql.functions import input_file_name

landing = dbutils.widgets.get("landing_path")
bronze = dbutils.widgets.get("bronze_path")
(spark.read.format("json").option("rescuedDataColumn", "_rescued_data").load(landing)
 .withColumn("source_file", input_file_name())
 .write.format("delta").mode("append").option("mergeSchema", "true").save(bronze))
