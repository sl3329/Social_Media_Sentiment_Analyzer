import sys
import json
from kafka import KafkaConsumer

if __name__ == "__main__":
    conn = '10.0.0.6:9092'
    queries = KafkaConsumer('test', bootstrap_servers=conn)

    for query in queries:
        print(query.value.decode("utf-8").strip())
