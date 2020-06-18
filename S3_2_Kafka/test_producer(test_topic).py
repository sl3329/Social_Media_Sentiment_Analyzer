from kafka import KafkaProducer
from kafka.errors import KafkaError
import boto3

# kafka producer
bootstrap_servers = 'localhost:9092, 10.0.0.4:9092, 10.0.0.12:9092'
topic = 'test'
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

# read data from s3
s3 = boto3.resource('s3')
bucket = s3.Bucket('tweetsdataset1')

for obj in bucket.objects.all():
    body = obj.get()['Body'].read().decode('utf-8')
    lines = body.split('\n')
    for line in lines:
        if line == "":
            continue
        try:
            producer.send(topic, value=line.encode('utf-8'))
        except KafkaError as e:
            print(e)
