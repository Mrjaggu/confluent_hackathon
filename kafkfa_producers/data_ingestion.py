from confluent_kafka import Producer
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from datetime import datetime
import json
import os

# MongoDB Setup
MONGO_URI = ""
DB_NAME = ""
COLLECTION_NAME = "users"

# Kafka Setup
TOPIC = "topic_users"

def read_kafka_config():
    config = {}
    with open("client.properties") as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.split("=", 1)
                config[parameter] = value.strip()
    return config

# Mongo doc cleaner for JSON serialization
def clean_document(doc):
    cleaned = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            cleaned[key] = str(value)
        elif isinstance(value, datetime):
            cleaned[key] = value.isoformat()
        elif isinstance(value, dict):
            cleaned[key] = clean_document(value)
        elif isinstance(value, list):
            cleaned[key] = [clean_document(item) if isinstance(item, dict) else item for item in value]
        else:
            cleaned[key] = value
    return cleaned

def mongo_to_kafka(producer, topic):
    print("🔌 Connecting to MongoDB...")
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    print(f"📤 Fetching documents from {DB_NAME}.{COLLECTION_NAME}...")
    for doc in collection.find():
        doc_clean = clean_document(doc)
        value_json = json.dumps(doc_clean)
        key = str(doc_clean.get("_id", ""))

        producer.produce(topic, key=key, value=value_json.encode('utf-8'))
        print(f"Sent doc with _id={key} to topic '{topic}'")

    producer.flush()
    print("All documents pushed to Kafka.")

def main():
    kafka_config = read_kafka_config()
    producer = Producer(kafka_config)
    mongo_to_kafka(producer, TOPIC)

if __name__ == "__main__":
    main()
