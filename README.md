# dds-512

pip install pandas numpy faker kafka-python cassandra-driver

CREATE KEYSPACE iot_data WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};


Databases Schema:
CREATE TABLE apple_watch_iot.device_metadata (
    device_id text PRIMARY KEY,
    model text,
    os_version text,
    battery_level int,
    last_sync_time timestamp
);
Partition Key: device_id ensures that each device's metadata is stored together.

------------------------------X-----------------------------------------------------X-------------------------------

CREATE TABLE apple_watch_iot.health_metrics (
    device_id text,
    timestamp timestamp,
    metric_type text,  -- e.g., 'heart_rate', 'calories_burned', 'sleep_quality'
    value float,
    unit text,         -- e.g., 'bpm', 'kcal', 'hours'
    PRIMARY KEY ((device_id), metric_type, timestamp)
) WITH CLUSTERING ORDER BY (metric_type ASC, timestamp DESC);

Partition Key: device_id ensures that all data for a specific device is stored together.
Clustering Columns: metric_type allows efficient querying of specific metrics, and timestamp ensures recent data is retrieved first.

------------------------------X-----------------------------------------------------X-------------------------------

CREATE TABLE apple_watch_iot.activity_tracking (
    device_id text,
    timestamp timestamp,
    activity_type text,  -- e.g., 'walking', 'running', 'cycling'
    value float,         -- e.g., steps, distance in meters
    unit text,           -- e.g., 'steps', 'meters', 'calories'
    PRIMARY KEY ((device_id), activity_type, timestamp)
) WITH CLUSTERING ORDER BY (activity_type ASC, timestamp DESC);
Partition Key: device_id ensures all activities for a device are grouped.
Clustering Columns: activity_type enables querying specific activities, and timestamp retrieves the most recent activities efficiently.

------------------------------X-----------------------------------------------------X-------------------------------

CREATE TABLE apple_watch_iot.environmental_data (
    device_id text,
    timestamp timestamp,
    data_type text,      -- e.g., 'temperature', 'humidity', 'location'
    value text,          -- Value depends on the data type (e.g., '25.3°C', '50%', 'latitude,longitude')
    PRIMARY KEY ((device_id), data_type, timestamp)
) WITH CLUSTERING ORDER BY (data_type ASC, timestamp DESC);

Partition Key: device_id groups all environmental data for a device.
Clustering Columns: data_type allows querying specific types of data (e.g., temperature, location), and timestamp ensures data is returned in chronological order.

------------------------------X-----------------------------------------------------X-------------------------------
CREATE TABLE apple_watch_iot.notifications (
    device_id text,
    timestamp timestamp,
    notification_type text,  -- e.g., 'message', 'reminder', 'alert'
    content text,            -- Notification message
    is_read boolean,
    PRIMARY KEY ((device_id), notification_type, timestamp)
) WITH CLUSTERING ORDER BY (notification_type ASC, timestamp DESC);
Partition Key: device_id ensures all notifications for a device are grouped together.
Clustering Columns: notification_type allows efficient retrieval by type, and timestamp retrieves recent notifications first.


Hello this is harsh