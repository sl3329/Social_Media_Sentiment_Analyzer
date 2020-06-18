import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 pyspark-shell'
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json

sc = SparkContext("spark://10.0.0.6:7077", appName="tweets")
sc.setLogLevel("WARN")
ssc = StreamingContext(sc, 2)
kvs = KafkaUtils.createDirectStream(ssc, ['tweets'], {"metadata.broker.list": '10.0.0.6:9092, 10.0.0.4:9092, 10.0.0.12:9092'})
tweets = kvs.map(lambda x: json.loads(x[1]))

tweets.ppprint()
ssc.start()
ssc.awaitTermination()
ssc.stop()
