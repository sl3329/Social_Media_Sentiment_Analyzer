import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 pyspark-shell'
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json
import re
from textblob import TextBlob
from psycopg2.pool import ThreadedConnectionPool

def find_tags(text):
    return re.findall('#\w+', text)

def clean_text(text):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split())

def get_sentiment(text):
    analysis = TextBlob(clean_text(text))
    # set sentiment 
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'

def get_df(tweet):
    text = tweet['text']
    tag_list = find_tags(text)
    word_list = [x for x in clean_text(text).split()]
    sentiment = get_sentiment(text)
    # tag_list is a list of tags
    # word_list is a list of words
    # sentiment can be "positive" or "neutral" or "negative"
    return [tag_list, word_list, sentiment]

def get_tag_sentiment(df):
    res = []
    for tag in df[0]:
        res.append(((tag, df[2]), 1))
    return res
def get_word_sentiment(df):
    res = []
    for word in df[1]:
        res.append(((word, df[2]), 1))
    return res

def save_sentiment(time, rdd):
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

def save_word_sentiment(time, rdd):
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

sc = SparkContext("spark://10.0.0.6:7077", appName="tweets")
sc.setLogLevel("WARN")
ssc = StreamingContext(sc, 2)
kvs = KafkaUtils.createDirectStream(ssc, ['tweets'], {"metadata.broker.list": '10.0.0.6:9092, 10.0.0.4:9092, 10.0.0.12:9092'})
tweets = kvs.map(lambda x: json.loads(x[1])).filter(lambda x: 'text' in x)
dataframe = tweets.map(get_df)


sentiment_count = dataframe.map(lambda x: (x[2], 1)).reduceByKey(lambda x, y: x + y)
tag_sentiment_count = dataframe.flatMap(get_tag_sentiment).reduceByKey(lambda x, y: x + y)
word_sentiment_count = dataframe.flatMap(get_word_sentiment).reduceByKey(lambda x, y: x + y)

sentiment_count.pprint(20)
tag_sentiment_count.pprint(20)
word_sentiment_count.pprint(20)

sentiment_count.foreachRDD(save_sentiment)
tag_sentiment_count.foreachRDD(save_tag_sentiment)
word_sentiment_count.foreachRDD(save_word_sentiment)

ssc.start()
ssc.awaitTermination()
ssc.stop()
