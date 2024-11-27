import argparse
import random
import time
from datetime import datetime, timedelta
import numpy as np
from faker import Faker
from kafka import KafkaProducer, KafkaConsumer
import json
from cassandra.cluster import Cluster
from cassandra_kafka_setup import BOOTSTRAP_SERVERS, TOPIC_NAME

# Argument Parser Setup
parser = argparse.ArgumentParser()
parser.add_argument(
    "--table", help="Specify the table to simulate data for", type=str, required=True
)
parser.add_argument(
    "--num_records", help="Number of records to generate", type=int, default=10
)
parser.add_argument(
    "--kafka_topic", help="Kafka topic name", type=str, default=TOPIC_NAME
)
args = parser.parse_args()

# Initialize Faker
fake = Faker()


# Generate data for different tables
def generate_device_metadata():
    return {
        "device_id": f"device_{random.randint(1, 1000):03}",
        "model": random.choice(
            ["Apple Watch Series 6", "Apple Watch SE", "Apple Watch Ultra"]
        ),
        "os_version": f"watchOS {random.randint(7, 10)}.{random.randint(0, 5)}",
        "battery_level": random.randint(10, 100),
        "last_sync_time": datetime.now().isoformat(),
    }


def generate_health_metrics():
    metrics = ["heart_rate", "calories_burned", "sleep_quality"]
    return {
        "device_id": f"device_{random.randint(1, 1000):03}",
        "timestamp": datetime.now().isoformat(),
        "metric_type": random.choice(metrics),
        "value": round(random.uniform(50, 200), 2),
        "unit": random.choice(["bpm", "kcal", "hours"]),
    }


def generate_activity_tracking():
    activities = ["walking", "running", "cycling"]
    return {
        "device_id": f"device_{random.randint(1, 1000):03}",
        "timestamp": datetime.now().isoformat(),
        "activity_type": random.choice(activities),
        "value": round(random.uniform(0, 10_000), 2),
        "unit": random.choice(["steps", "meters", "calories"]),
    }


def generate_environmental_data():
    data_types = ["temperature", "humidity", "location"]
    return {
        "device_id": f"device_{random.randint(1, 1000):03}",
        "timestamp": datetime.now().isoformat(),
        "data_type": random.choice(data_types),
        "value": (
            fake.latitude_longitude()
            if "location"
            else f"{random.uniform(15, 35):.2f}°C"
        ),
    }


def generate_notifications():
    notification_types = ["message", "reminder", "alert"]
    return {
        "device_id": f"device_{random.randint(1, 1000):03}",
        "timestamp": datetime.now().isoformat(),
        "notification_type": random.choice(notification_types),
        "content": fake.sentence(),
        "is_read": random.choice([True, False]),
    }


def generate_device_status_logs():
    return {
        "device_id": f"device_{random.randint(1, 1000):03}",
        "timestamp": datetime.now().isoformat(),
        "status_code": random.choice(["active", "inactive", "error"]),
        "description": fake.sentence(),
        "battery_health": random.choice(["Good", "Needs Service"]),
    }


def generate_gps_location_data():
    return {
        "device_id": f"device_{random.randint(1, 1000):03}",
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


# Kafka Consumer setup
def setup_kafka_consumer(topic):
    return KafkaConsumer(
        topic,
        bootstrap_servers=[BOOTSTRAP_SERVERS],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="iot-consumer-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )


# Cassandra session setup
def setup_cassandra_session():
    cluster = Cluster(["127.0.0.1"])
    session = cluster.connect()
    session.set_keyspace("apple_watch_iot")
    return session


# Insert data into Cassandra
def send_to_cassandra(session, table, data):
    if table == "device_metadata":
        query = f"""
        INSERT INTO device_metadata 
        (device_id, model, os_version, battery_level, last_sync_time) 
        VALUES ('{data['device_id']}', '{data['model']}', '{data['os_version']}', 
        {data['battery_level']}, '{data['last_sync_time']}');
        """
    elif table == "health_metrics":
        query = f"""
        INSERT INTO health_metrics 
        (device_id, timestamp, metric_type, value, unit) 
        VALUES ('{data['device_id']}', '{data['timestamp']}', '{data['metric_type']}', 
        {data['value']}, '{data['unit']}');
        """
    elif table == "activity_tracking":
        query = f"""
        INSERT INTO activity_tracking 
        (device_id, timestamp, activity_type, value, unit) 
        VALUES ('{data['device_id']}', '{data['timestamp']}', '{data['activity_type']}', 
        {data['value']}, '{data['unit']}');
        """
    elif table == "environmental_data":
        query = f"""
        INSERT INTO environmental_data 
        (device_id, timestamp, data_type, value) 
        VALUES ('{data['device_id']}', '{data['timestamp']}', '{data['data_type']}', 
        '{data['value']}');
        """
    elif table == "notifications":
        query = f"""
        INSERT INTO notifications 
        (device_id, timestamp, notification_type, content, is_read) 
        VALUES ('{data['device_id']}', '{data['timestamp']}', '{data['notification_type']}', 
        '{data['content']}', {data['is_read']});
        """
    elif table == "device_status_logs":
        query = f"""
        INSERT INTO device_status_logs 
        (device_id, timestamp, status_code, description, battery_health) 
        VALUES ('{data['device_id']}', '{data['timestamp']}', '{data['status_code']}', 
        '{data['description']}', '{data['battery_health']}');
        """
    elif table == "gps_location_data":
        query = f"""
        INSERT INTO gps_location_data 
        (device_id, timestamp, latitude, longitude, altitude) 
        VALUES ('{data['device_id']}', '{data['timestamp']}', {data['latitude']}, 
        {data['longitude']}, {data['altitude']});
        """
    session.execute(query)
    print(f"Inserted into Cassandra ({table}): {data}")


def send_to_kafka(producer, data):
    producer.send(TOPIC_NAME, value=data)
    print(f"Sent to Kafka: {data}")
    time.sleep(0.1)  # Simulate delay between readings


# Main function
if __name__ == "__main__":
    if args.table not in table_map:
        print(f"Invalid table name. Choose from: {', '.join(table_map.keys())}")
        exit(1)

    generate_data = table_map[args.table]
    producer = setup_kafka_producer()
    consumer = setup_kafka_consumer(args.kafka_topic)
    session = setup_cassandra_session()

    # Producer: Generate and send data to Kafka
    for _ in range(args.num_records):
        data = generate_data()
        send_to_kafka(producer, data)
        # producer.send(args.kafka_topic, value=data)
        print(f"Sent to Kafka: {data}")
    
    producer.close()

    # Consumer: Read from Kafka and insert into Cassandra
    print("Starting Kafka consumer...")
    for message in consumer:
        data = message.value
        send_to_cassandra(session, args.table, data)
