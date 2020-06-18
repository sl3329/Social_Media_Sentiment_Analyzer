import pandas as pd
import psycopg2
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import pandas as pd
import plotly.offline as pyo
import time

conn = psycopg2.connect(host='ec2-54-243-112-184.compute-1.amazonaws.com', database='tweetsdata', user='shan', password='password')
c = conn.cursor()



df = pd.read_sql("SELECT * FROM tag_sentiment WHERE sentiment = 'positive' ORDER BY count DESC LIMIT 20", conn)
print(df)