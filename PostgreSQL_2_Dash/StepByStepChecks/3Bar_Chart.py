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

conn = psycopg2.connect(host='ec2-54-243-112-184.compute-1.amazonaws.com', database='tweetsdata', user='shan', password='password')
c = conn.cursor()

df_postive = pd.read_sql("SELECT * FROM sentiment WHERE sentiment = 'positive' ORDER BY equip_id DESC LIMIT 20", conn)
df_postive.sort_values('equip_id', inplace=True)

df_negative = pd.read_sql("SELECT * FROM sentiment WHERE sentiment = 'negative' ORDER BY equip_id DESC LIMIT 20", conn)
df_negative.sort_values('equip_id', inplace=True)

df_neutral = pd.read_sql("SELECT * FROM sentiment WHERE sentiment = 'neutral' ORDER BY equip_id DESC LIMIT 20", conn)
df_neutral.sort_values('equip_id', inplace=True)

trace_postive = go.Bar(x=df_postive['timestamp'], y=df_postive['count'],name='postive',marker={'color':'#faafc0'})
trace_negative = go.Bar(x=df_negative['timestamp'], y=df_negative['count'],name='negative',marker={'color':'#f2faaf'})
trace_neutral = go.Bar(x=df_neutral['timestamp'], y=df_neutral['count'],name='neutral',marker={'color':'#70deff'})

app = dash.Dash()

colors = {'background':'#111111','text':'#7FDBFF'}

data = [trace_neutral, trace_postive, trace_negative]
layout = go.Layout(title='bars',barmode='stack')
fig = go.Figure(data=data,layout=layout)
pyo.plot(fig)


if __name__ == '__main__':
	app.run_server(debug=True)
