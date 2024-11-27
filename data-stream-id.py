import random
import time
from datetime import datetime, timedelta
from faker import Faker
import json
import pandas as pd
from cassandra.cluster import Cluster
from kafka import KafkaProducer

# Constants for Kafka
BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC_NAME = "apple-watch-iot-2"

fake = Faker()

# Define states and towns
STATES = {
    "Arizona": ["Tempe", "Phoenix", "Scottsdale"],
    "California": ["Los Angeles", "San Francisco", "San Diego"],
    "Texas": ["Austin", "Dallas", "Houston"],
    "New York": ["New York City", "Buffalo", "Rochester"],
}

# Assign a town and state to each device ID
DEVICE_LOCATIONS = {}
device_ids = [f"device_{i:03}" for i in range(1, 21)]  # 20 unique device IDs
states_and_towns = []

# Flatten the STATES dictionary into a list of (state, town) tuples
for state, towns in STATES.items():
    for town in towns:
        states_and_towns.append((state, town))

# Assign each device to a random state and town
for device_id in device_ids:
    state, town = random.choice(states_and_towns)
    # Assign approximate lat/lon for each town
    town_coords = {
        "Tempe": (33.4255, -111.9400),
        "Phoenix": (33.4484, -112.0740),
        "Scottsdale": (33.4942, -111.9261),
        "Los Angeles": (34.0522, -118.2437),
        "San Francisco": (37.7749, -122.4194),
        "San Diego": (32.7157, -117.1611),
        "Austin": (30.2672, -97.7431),
        "Dallas": (32.7767, -96.7970),
        "Houston": (29.7604, -95.3698),
        "New York City": (40.7128, -74.0060),
        "Buffalo": (42.8864, -78.8784),
        "Rochester": (43.1566, -77.6088),
    }
    latitude, longitude = town_coords.get(town, (fake.latitude(), fake.longitude()))
    DEVICE_LOCATIONS[device_id] = {
        "state": state,
        "town": town,
        "latitude": latitude,
        "longitude": longitude,
    }

# Define activities and related metrics
ACTIVITY_DATA = {
    "biking": {"calories_per_min": 7, "heart_rate": (120, 160), "stress_level": 5},
    "walking": {"calories_per_min": 4, "heart_rate": (80, 110), "stress_level": 2},
    "running": {"calories_per_min": 10, "heart_rate": (140, 180), "stress_level": 6},
    "sleeping": {"calories_per_min": 1, "heart_rate": (50, 70), "stress_level": 1},
    "working": {"calories_per_min": 2, "heart_rate": (60, 80), "stress_level": 7},
}

# Generate weather for a specific town (relatively stable)
def generate_weather(town):
    random.seed(town)  # Ensure consistent weather per town
    return {
        "temperature": f"{random.uniform(20, 30):.1f}°C",
        "humidity": f"{random.uniform(40, 60):.1f}%",
    }

def generate_data_for_device(device_id):
    device_location = DEVICE_LOCATIONS[device_id]
    town = device_location["town"]
    state = device_location["state"]
    latitude = device_location["latitude"]
    longitude = device_location["longitude"]

    data = []
    base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    for i in range(5):  # Generate 5 entries per device
        current_time = base_time + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))

        activity = random.choice(list(ACTIVITY_DATA.keys()))
        activity_data = ACTIVITY_DATA[activity]
        heart_rate = random.randint(*activity_data["heart_rate"])
        duration = random.randint(10, 60)  # Duration between 10 to 60 minutes
        calories_burned = activity_data["calories_per_min"] * duration
        stress_level = activity_data["stress_level"]

        # Add health metrics
        data.append(
            {
                "device_id": device_id,
                "timestamp": current_time.isoformat(),
                "metric_type": "heart_rate",
                "value": heart_rate,
                "unit": "bpm",
            }
        )
        data.append(
            {
                "device_id": device_id,
                "timestamp": current_time.isoformat(),
                "metric_type": "calories_burned",
                "value": calories_burned,
                "unit": "kcal",
            }
        )
        data.append(
            {
                "device_id": device_id,
                "timestamp": current_time.isoformat(),
                "metric_type": "stress_level",
                "value": stress_level,
                "unit": "level",
            }
        )

        # Add location data
        data.append(
            {
                "device_id": device_id,
                "timestamp": current_time.isoformat(),
                "data_type": "location",
                "value": f"{latitude:.6f}, {longitude:.6f}",
                "town": town,
                "state": state,
            }
        )

        # Add weather data
        weather = generate_weather(town)
        data.append(
            {
                "device_id": device_id,
                "timestamp": current_time.isoformat(),
                "data_type": "temperature",
                "value": weather["temperature"],
            }
        )
        data.append(
            {
                "device_id": device_id,
                "timestamp": current_time.isoformat(),
                "data_type": "humidity",
                "value": weather["humidity"],
            }
        )
    return data

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
    if table == "health_metrics":
        query = f"""
        INSERT INTO {table} (device_id, timestamp, metric_type, value, unit) 
        VALUES (%s, %s, %s, %s, %s);
        """
        session.execute(query, (data["device_id"], data["timestamp"], data["metric_type"], data["value"], data["unit"]))
    elif table == "environmental_data":
        query = f"""
        INSERT INTO environmental_data (device_id, timestamp, data_type, value, town, state) 
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        session.execute(query, (data["device_id"], data["timestamp"], data["data_type"], data["value"], data.get("town", ""), data.get("state", "")))
    else:
        print(f"Unknown table: {table}")
    print(f"Inserted into Cassandra ({table}): {data}")

# Send data to Kafka
def send_to_kafka(producer, data):
    producer.send(TOPIC_NAME, value=data)
    print(f"Sent to Kafka: {data}")
    time.sleep(0.01)  # Reduced delay for faster data generation

# Write data to CSV
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

    health_metrics_data = []
    location_data = []

    for device_id in DEVICE_LOCATIONS.keys():
        device_data = generate_data_for_device(device_id)
        for entry in device_data:
            if entry.get("metric_type") in ["heart_rate", "calories_burned", "stress_level"]:
                health_metrics_data.append(entry)
                send_to_cassandra(session, "health_metrics", entry)
            elif entry.get("data_type") == "location":
                location_data.append(entry)
                send_to_cassandra(session, "environmental_data", entry)
            else:
                # For other environmental data like temperature and humidity
                send_to_cassandra(session, "environmental_data", entry)

            # Send all entries to Kafka
            send_to_kafka(producer, entry)

    # Optionally, write to CSV
    write_to_csv(health_metrics_data, "health_metrics")
    write_to_csv(location_data, "environmental_data")

    producer.close()
