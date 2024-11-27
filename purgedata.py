from cassandra.cluster import Cluster
from kafka.admin import KafkaAdminClient, NewTopic
import os
import glob

# Constants
CASSANDRA_HOST = "127.0.0.1"
KEYSPACE = "apple_watch_iot"
BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC_NAME = "apple-watch-iot-2"

def purge_cassandra_data():
    try:
        cluster = Cluster([CASSANDRA_HOST])
        session = cluster.connect()

        # Drop the keyspace
        drop_keyspace_query = f"DROP KEYSPACE IF EXISTS {KEYSPACE};"
        session.execute(drop_keyspace_query)
        print(f"Cassandra keyspace '{KEYSPACE}' dropped successfully.")

    except Exception as e:
        print(f"Error dropping Cassandra keyspace '{KEYSPACE}': {e}")

    finally:
        session.shutdown()
        cluster.shutdown()

def purge_kafka_topic():
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            client_id="kafka_purge_script"
        )

        # Delete the Kafka topic
        admin_client.delete_topics([TOPIC_NAME])
        print(f"Kafka topic '{TOPIC_NAME}' deleted successfully.")

    except Exception as e:
        print(f"Error deleting Kafka topic '{TOPIC_NAME}': {e}")

    finally:
        admin_client.close()

def delete_csv_files():
    try:
        csv_files = glob.glob("*.csv")
        for file in csv_files:
            os.remove(file)
            print(f"Deleted CSV file: {file}")

    except Exception as e:
        print(f"Error deleting CSV files: {e}")

if __name__ == "__main__":
    confirm = input("Are you sure you want to purge all data? This action cannot be undone. (yes/no): ")
    if confirm.lower() == "yes":
        print("Purging Cassandra data...")
        purge_cassandra_data()

        print("Purging Kafka topic...")
        purge_kafka_topic()

        print("Deleting generated CSV files...")
        delete_csv_files()

        print("Data purge completed successfully.")
    else:
        print("Data purge canceled.")
