# Customer tracking store

The production container uses `/parcel_id` as its partition key and stores exactly one latest-state document per parcel. The tracking API therefore uses a single-partition point read: `read_item(id=parcel_id, partition_key=parcel_id)`. This is the lowest-cost predictable lookup pattern and avoids cross-partition queries.

For the free tier, start with 1,000 RU/s and monitor normalized RU consumption, 429 throttles, and logical-partition size. A hash-like parcel identifier spreads writes naturally; do not use hub ID because a busy hub would become a hot partition. The local demo writes the same document shape to JSONL.
