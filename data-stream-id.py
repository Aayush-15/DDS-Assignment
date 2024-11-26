import random
import time
from datetime import datetime
from faker import Faker
from kafka import KafkaProducer
import json
import pandas as pd
from cassandra.cluster import Cluster
from cassandra_kafka_setup import BOOTSTRAP_SERVERS, TOPIC_NAME
from decimal import Decimal

# Initialize Faker
fake = Faker()


def decimal_default(obj):
    """Custom serializer for Decimal objects."""
    if isinstance(obj, Decimal):
        return float(obj)  # Convert Decimal to float
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Generate data for different tables
def generate_device_metadata(device_id):
    return {
        "device_id": f"device_{device_id:03}",
        "model": random.choice(
            ["Apple Watch Series 6", "Apple Watch SE", "Apple Watch Ultra"]
        ),
        "os_version": f"watchOS {random.randint(7, 10)}.{random.randint(0, 5)}",
        "battery_level": random.randint(10, 100),
        "last_sync_time": datetime.now().isoformat(),
    }


def generate_health_metrics(device_id):
    metrics = ["heart_rate", "calories_burned", "sleep_quality"]
    return {
        "device_id": f"device_{device_id:03}",
        "timestamp": datetime.now().isoformat(),
        "metric_type": random.choice(metrics),
        "value": round(random.uniform(50, 200), 2),
        "unit": random.choice(["bpm", "kcal", "hours"]),
    }


def generate_activity_tracking(device_id):
    activities = ["walking", "running", "cycling"]
    return {
        "device_id": f"device_{device_id:03}",
        "timestamp": datetime.now().isoformat(),
        "activity_type": random.choice(activities),
        "value": round(random.uniform(0, 10_000), 2),
        "unit": random.choice(["steps", "meters", "calories"]),
    }


def generate_environmental_data(device_id):
    data_types = ["temperature", "humidity", "location"]
    data_type = random.choice(data_types)
    if data_type == "location":
        value = f"{fake.latitude():.6f}, {fake.longitude():.6f}"
    else:
        value = f"{random.uniform(15, 35):.2f}°C" if data_type == "temperature" else f"{random.uniform(40, 90):.1f}%"
    return {
        "device_id": f"device_{device_id:03}",
        "timestamp": datetime.now().isoformat(),
        "data_type": data_type,
        "value": value,
    }




def generate_notifications(device_id):
    notification_types = ["message", "reminder", "alert"]
    return {
        "device_id": f"device_{device_id:03}",
        "timestamp": datetime.now().isoformat(),
        "notification_type": random.choice(notification_types),
        "content": fake.sentence(),
        "is_read": random.choice([True, False]),
    }


def generate_device_status_logs(device_id):
    return {
        "device_id": f"device_{device_id:03}",
        "timestamp": datetime.now().isoformat(),
        "status_code": random.choice(["active", "inactive", "error"]),
        "description": fake.sentence(),
        "battery_health": random.choice(["Good", "Needs Service"]),
    }


def generate_gps_location_data(device_id):
    return {
        "device_id": f"device_{device_id:03}",
        "timestamp": datetime.now().isoformat(),
        "latitude": round(fake.latitude(), 6),
        "longitude": round(fake.longitude(), 6),
        "altitude": round(random.uniform(0, 5000), 2),
    }


# Table-to-function mapping
table_map = {
    "device_metadata": generate_device_metadata,
    "health_metrics": generate_health_metrics,
    "activity_tracking": generate_activity_tracking,
    "environmental_data": generate_environmental_data,
    "notifications": generate_notifications,
    "device_status_logs": generate_device_status_logs,
    "gps_location_data": generate_gps_location_data,
}


# Kafka Producer setup
def setup_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=[BOOTSTRAP_SERVERS],
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
    )


# Cassandra session setup
def setup_cassandra_session():
    cluster = Cluster(["127.0.0.1"])
    session = cluster.connect()
    session.set_keyspace("apple_watch_iot")
    return session


# Insert data into Cassandra
def send_to_cassandra(session, table, data):
    query = f"""
    INSERT INTO {table} ({', '.join(data.keys())}) 
    VALUES ({', '.join(['%s'] * len(data))});
    """
    session.execute(query, tuple(data.values()))
    print(f"Inserted into Cassandra ({table}): {data}")


def send_to_kafka(producer, data):
    producer.send(TOPIC_NAME, value=data)
    print(f"Sent to Kafka: {data}")
    time.sleep(0.1)  # Simulate delay between readings


def write_to_csv(data_list, table_name):
    """Write data to a CSV file for the specified table."""
    filename = f"{table_name}.csv"
    df = pd.DataFrame(data_list)
    df.to_csv(filename, index=False)
    print(f"Data for table '{table_name}' written to CSV file: {filename}")


# Main function
if __name__ == "__main__":
    producer = setup_kafka_producer()
    session = setup_cassandra_session()

    for table, generate_function in table_map.items():
        all_data = []  # Collect all data for this table
        for device_id in range(1, 51):  # Device IDs from 1 to 50
            data = generate_function(device_id)
            all_data.append(data)
            send_to_kafka(producer, data)
            send_to_cassandra(session, table, data)

        # Write all data for this table to a CSV file
        write_to_csv(all_data, table)

    producer.close()
