-- Azure SQL reporting mart (local demo uses equivalent SQLite DDL in load_mart.py)
CREATE TABLE dim_hub (hub_key INT IDENTITY PRIMARY KEY, hub_id VARCHAR(20) NOT NULL UNIQUE);
CREATE TABLE dim_lane (lane_key INT IDENTITY PRIMARY KEY, lane_id VARCHAR(50) NOT NULL UNIQUE, origin_hub VARCHAR(20), destination_hub VARCHAR(20));
CREATE TABLE dim_date (date_key INT PRIMARY KEY, calendar_date DATE NOT NULL UNIQUE);
CREATE TABLE fct_sla (
  parcel_id VARCHAR(32) PRIMARY KEY, lane_key INT NOT NULL, pickup_date_key INT NOT NULL,
  status VARCHAR(32) NOT NULL, promised_hours INT NOT NULL, actual_hours DECIMAL(10,2),
  breach_flag BIT NOT NULL, exception_reason VARCHAR(64),
  FOREIGN KEY (lane_key) REFERENCES dim_lane(lane_key), FOREIGN KEY (pickup_date_key) REFERENCES dim_date(date_key)
);
CREATE INDEX ix_fct_sla_lane_date ON fct_sla(lane_key, pickup_date_key) INCLUDE (breach_flag, actual_hours);
