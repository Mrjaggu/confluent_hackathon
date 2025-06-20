from crewai_tools import BaseTool
from confluent_kafka import Consumer
from pydantic import PrivateAttr
import json

class KafkaDataTool(BaseTool):
    name: str = "KafkaDataTool"
    description: str = "Tool to access users, movies, theaters, comments from Kafka"

    _config: dict = PrivateAttr()
    _consumer: Consumer = PrivateAttr()

    def __init__(self, config_file="client.properties"):
        super().__init__()
        self._config = self._read_config(config_file)
        self._config["group.id"] = "crewai-data-tool-11"
        self._config["auto.offset.reset"] = "earliest"
        self._consumer = Consumer(self._config)

    def _read_config(self, file):
        config = {}
        with open(file) as fh:
            for line in fh:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    config[key] = value
        return config

    def _lookup(self, topic, match_key, match_value):
        self._consumer.subscribe([topic])
        for _ in range(100):  # Poll limit
            msg = self._consumer.poll(0.5)
            if msg is None or msg.error():
                continue
            try:
                val = json.loads(msg.value().decode("utf-8"))
                if val.get(match_key) == match_value:
                    return json.dumps(val)
            except Exception:
                continue
        return "{}"

    def _run(self, input: str) -> str:
        """
        Format: user:<user_id>, movie:<movie_id>, theater:<location>, comment:<keyword>
        """
        try:
            prefix, value = input.split(":", 1)
            value = value.strip()

            if prefix == "user":
                return self._lookup("topic_users", "user_id", value)

            elif prefix == "movie":
                return self._lookup("topic_movies", "movie_id", value)

            elif prefix == "theater":
                return self._lookup("topic_theaters", "location", value)

            elif prefix == "comment":
                return self._lookup("topic_comments", "text", value)

            else:
                return "Invalid input format"
        except Exception as e:
            return f"Error: {str(e)}"
