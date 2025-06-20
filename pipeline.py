from confluent_kafka import Consumer, Producer
import json
from agents.crew_config import movie_crew  # use crew instead of separate agents

def read_config():
    config = {}
    with open("client.properties") as fh:
        for line in fh:
            if "=" in line and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                config[key] = val
    return config

def run_pipeline():
    config = read_config()
    config["group.id"] = "movie-crew-pipeline-5"
    config["auto.offset.reset"] = "earliest"

    consumer = Consumer(config)
    producer = Producer(config)
    consumer.subscribe(["movie_queries"])

    while True:
        msg = consumer.poll(1.0)
        if msg is None or msg.error():
            continue

        query_obj = json.loads(msg.value().decode("utf-8"))
        user_id = query_obj.get("user_id")
        query = query_obj.get("prompt")
        print(f"🔍 Query from {user_id}: {query}")

        try:
            # 🔁 CrewAI execution
            final_summary = movie_crew.kickoff(inputs={"input": query})
            print('Agent output:',final_summary)

            result = {
                "user_id": user_id,
                "query": query,
                "summary": final_summary.raw
            }
            print(result)
            producer.produce("movie_insights", value=json.dumps(result).encode("utf-8"))
            producer.flush()
            print("✅ Published to movie_insights")

        except Exception as e:
            print("❌ Error in Crew pipeline:", str(e))

if __name__ == "__main__":
    run_pipeline()
