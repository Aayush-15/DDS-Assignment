from cassandra.cluster import Cluster
from kafka.admin import KafkaAdminClient, NewTopic

BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC_NAME = "apple-watch-iot-5"
NUM_PARTITIONS = 3
REPLICATION_FACTOR = 1

def create_keyspace_and_tables():
    # Connect to Cassandra
    cluster = Cluster(["127.0.0.1"])
    session = cluster.connect()

    # Create Keyspace
    session.execute(
        """
    CREATE KEYSPACE IF NOT EXISTS apple_watch_iot
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
    """
    )

    # Use the Keyspace
    session.set_keyspace("apple_watch_iot")

    # Create Tables
    session.execute(
        """
    CREATE TABLE IF NOT EXISTS device_metadata (
        device_id text PRIMARY KEY,
        model text,
        os_version text,
        battery_level int,
        last_sync_time timestamp
    );
    """
    )

    session.execute(
        """
    CREATE TABLE IF NOT EXISTS health_metrics (
        device_id text,
        timestamp timestamp,
        metric_type text,  -- e.g., 'heart_rate', 'calories_burned', 'stress_level'
        value float,
        unit text,         -- e.g., 'bpm', 'kcal', 'level'
        PRIMARY KEY ((device_id), metric_type, timestamp)
    ) WITH CLUSTERING ORDER BY (metric_type ASC, timestamp DESC);
    """
    )

    session.execute(
        """
    CREATE TABLE IF NOT EXISTS activity_tracking (
        device_id text,
        timestamp timestamp,
        activity_type text,  -- e.g., 'walking', 'running', 'cycling'
        value float,         -- e.g., steps, distance in meters
        unit text,           -- e.g., 'steps', 'meters', 'calories'
        PRIMARY KEY ((device_id), activity_type, timestamp)
    ) WITH CLUSTERING ORDER BY (activity_type ASC, timestamp DESC);
    """
    )

    session.execute(
        """
    CREATE TABLE IF NOT EXISTS environmental_data (
        device_id text,
        timestamp timestamp,
        data_type text,      -- e.g., 'temperature', 'humidity', 'location'
        value text,          -- Value depends on the data type (e.g., '25.3°C', '50%', 'latitude,longitude (location_name)')
        town text,
        state text,
        PRIMARY KEY ((device_id), data_type, timestamp)
    ) WITH CLUSTERING ORDER BY (data_type ASC, timestamp DESC);
    """
    )

    session.execute(
        """
    CREATE TABLE IF NOT EXISTS notifications (
        device_id text,
        timestamp timestamp,
        notification_type text,  -- e.g., 'message', 'reminder', 'alert'
        content text,            -- Notification message
        is_read boolean,
        PRIMARY KEY ((device_id), notification_type, timestamp)
    ) WITH CLUSTERING ORDER BY (notification_type ASC, timestamp DESC);
    """
    )

    session.execute(
        """
    CREATE TABLE IF NOT EXISTS device_status_logs (
        device_id text,
        timestamp timestamp,
        status_code text,       -- e.g., 'active', 'inactive', 'error'
        description text,       -- Detailed status description
        battery_health text,    -- e.g., 'Good', 'Needs Service'
        PRIMARY KEY ((device_id), timestamp)
    ) WITH CLUSTERING ORDER BY (timestamp DESC);
    """
    )

    print("Keyspace and tables created successfully.")

def create_kafka_topic(
    bootstrap_servers, topic_name, num_partitions, replication_factor
):
    try:
        # Initialize Kafka Admin Client
        admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers, client_id="kafka_topic_creator"
        )

        # Define the new topic
        topic = NewTopic(
            name=topic_name,
            num_partitions=num_partitions,
            replication_factor=replication_factor,
        )

        # Create the topic
        admin_client.create_topics(new_topics=[topic], validate_only=False)
        print(f"Kafka topic '{topic_name}' created successfully!")

    except Exception as e:
        print(f"Error creating Kafka topic '{topic_name}': {e}")

    finally:
        admin_client.close()

if __name__ == "__main__":
    create_keyspace_and_tables()

    # Create Kafka topic
    create_kafka_topic(
        BOOTSTRAP_SERVERS, TOPIC_NAME, NUM_PARTITIONS, REPLICATION_FACTOR
    )
