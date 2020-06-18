import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 pyspark-shell'
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json
import re
from textblob import TextBlob
from psycopg2.pool import ThreadedConnectionPool

class Streamer():

    def __init__(self):
        """
        Initialize Spark, Spark streaming context
        """
        self.sc = SparkContext("spark://10.0.0.6:7077", appName="tweets")
        self.sc.setLogLevel("WARN")
        self.ssc = StreamingContext(self.sc, 2)
        self.kvs = KafkaUtils.createDirectStream(self.ssc, ['tweets'], {"metadata.broker.list": '10.0.0.6:9092, 10.0.0.4:9092, 10.0.0.12:9092'})
        self.tweets = self.kvs.map(lambda x: json.loads(x[1])).filter(lambda x: 'text' in x)
        self.dataframe = self.tweets.map(self.get_df)

    # find_tags is to find tags (the word with "#") in a text 
    def find_tags(self, text):
        return re.findall('#\w+', text)

    # clean_text is to get clean text (without punctuation and links)
    def clean_text(self, text):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split())

    # get_sentiment is to get the sentiment (positive/neutral/negative) of a text
    def get_sentiment(self, text):
        analysis = TextBlob(self.clean_text(text))
        # set sentiment 
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    # get_df is to get data from kafka and manipulate data into dataframe with required info
    def get_df(self, tweet):
        '''
        tag_list is a list of tags
        word_list is a list of words
        sentiment can be "positive" or "neutral" or "negative"
        '''
        text = tweet['text']
        tag_list = self.find_tags(text)
        word_list = [x for x in self.clean_text(text).split()]
        sentiment = self.get_sentiment(text)
        return [tag_list, word_list, sentiment]

    # get_tag_sentiment is to get sentiment for each tag
    def get_tag_sentiment(self, df):
        res = []
        for tag in df[0]:
            res.append(((tag, df[2]), 1))
        return res

    # get_word_sentiment is to get sentiment for each word
    def get_word_sentiment(self, df):
        res = []
        for word in df[1]:
            res.append(((word, df[2]), 1))
        return res

    # save_sentiment is to save the sentiment data into sentiment table
    def save_sentiment(self, time, rdd):
        def save_partition(iter):
            pool = ThreadedConnectionPool(1,
                                          5,
                                          database='tweetsdata',
                                          user='shan',
                                          password='password',
                                          host='10.0.0.6',
                                          port='5432')
            conn = pool.getconn()
            cur = conn.cursor()

            for record in iter:
                qry = "INSERT INTO sentiment (timestamp, sentiment, count) VALUES ('%s','%s',%s);" % (
                    time, record[0], record[1])
                cur.execute(qry)

            conn.commit()
            cur.close()
            pool.putconn(conn)

        rdd.foreachPartition(save_partition)

    # save_tag_sentiment is to save the sentiment of each tag into tag_sentiment table
    def save_tag_sentiment(time, rdd):
        def save_partition(iter):
            pool = ThreadedConnectionPool(1,
                                          5,
                                          database='tweetsdata',
                                          user='shan',
                                          password='password',
                                          host='10.0.0.6',
                                          port='5432')
            conn = pool.getconn()
            cur = conn.cursor()

            for record in iter:
                qry = "INSERT INTO tag_sentiment (timestamp, tag, sentiment, count) VALUES ('%s','%s', '%s', %s);" % (
                    time, record[0][0], record[0][1], record[1])
                cur.execute(qry)

            conn.commit()
            cur.close()
            pool.putconn(conn)

        rdd.foreachPartition(save_partition)

    # save_tag_sentiment is to save the sentiment of each word into word_sentiment table
    def save_word_sentiment(self, time, rdd):
        def save_partition(iter):
            pool = ThreadedConnectionPool(1,
                                          5,
                                          database='tweetsdata',
                                          user='shan',
                                          password='password',
                                          host='10.0.0.6',
                                          port='5432')
            conn = pool.getconn()
            cur = conn.cursor()

            for record in iter:
                qry = "INSERT INTO word_sentiment (timestamp, word, sentiment, count) VALUES ('%s','%s', '%s', %s);" % (
                    time, record[0][0], record[0][1], record[1])
                cur.execute(qry)

            conn.commit()
            cur.close()
            pool.putconn(conn)

        rdd.foreachPartition(save_partition)

    # init_stream is to Initialize Spark, Spark streaming context
    def init_stream(self):
        sentiment_count = self.dataframe.map(lambda x: (x[2], 1)).reduceByKey(lambda x, y: x + y)
        tag_sentiment_count = self.dataframe.flatMap(self.get_tag_sentiment).reduceByKey(lambda x, y: x + y)
        word_sentiment_count = self.dataframe.flatMap(self.get_word_sentiment).reduceByKey(lambda x, y: x + y)

        sentiment_count.pprint(20)
        tag_sentiment_count.pprint(20)
        word_sentiment_count.pprint(20)

        sentiment_count.foreachRDD(self.save_sentiment)
        tag_sentiment_count.foreachRDD(self.save_tag_sentiment)
        word_sentiment_count.foreachRDD(self.save_word_sentiment)

    # start_stream is to start the streaming process 
    def start_stream(self):
        self.init_stream()
        self.ssc.start()
        self.ssc.awaitTermination()
        self.ssc.stop()

if __name__ == "__main__":
    streamer = Streamer()
    streamer.start_stream()
