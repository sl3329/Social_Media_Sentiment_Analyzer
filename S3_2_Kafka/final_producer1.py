from kafka import KafkaProducer
from kafka.errors import KafkaError
import boto3

''' connect to 3 kafka brokers, produce data into topic "tweets",
    and read data from s3 bucket'''

bootstrap_servers = 'localhost:9092, 10.0.0.4:9092, 10.0.0.12:9092'
topic = 'tweets'
s3 = boto3.resource('s3')

class Producer():

    def __init__(self):
        '''
        Initialize Kafka Producer
        '''
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        self.bucket = s3.Bucket('tweetsdataset1')

    def produce_msgs(self):
        for obj in self.bucket.objects.all():
            body = obj.get()['Body'].read().decode('utf-8')
            lines = body.split('\n')
            for line in lines:
                if line == "":
                    continue
                try:
                    self.producer.send(topic, value=line.encode('utf-8'))
                except KafkaError as e:
                    print(e)


if __name__ == "__main__":
    prod = Producer()
    prod.produce_msgs()
