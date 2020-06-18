import pandas as pd
import psycopg2
import dash
from dash.dependencies import Output, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import pandas as pd
import plotly.offline as pyo

app = dash.Dash(__name__)
app.layout = html.Div(
	[
		dcc.Graph(id='live-graph', animate=True),
		dcc.Interval(
			id='graph-update',
			interval=2*1000
		),

	]
)

conn = psycopg2.connect(host='ec2-54-243-112-184.compute-1.amazonaws.com', database='tweetsdata', user='shan', password='password')
c = conn.cursor()

df_postive = pd.read_sql("SELECT * FROM sentiment WHERE sentiment = 'positive' ORDER BY equip_id DESC LIMIT 30", conn)
df_postive.sort_values('equip_id', inplace=True)

df_negative = pd.read_sql("SELECT * FROM sentiment WHERE sentiment = 'negative' ORDER BY equip_id DESC LIMIT 30", conn)
df_negative.sort_values('equip_id', inplace=True)

df_neutral = pd.read_sql("SELECT * FROM sentiment WHERE sentiment = 'neutral' ORDER BY equip_id DESC LIMIT 30", conn)
df_neutral.sort_values('equip_id', inplace=True)

# df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
print(df_postive)
print(df_negative)

X_postive = df_postive['timestamp']
Y_postive = df_postive['count']
X_negative = df_negative['timestamp']
Y_negative = df_negative['count']
X_neutral = df_neutral['timestamp']
Y_neutral = df_neutral['count']

trace_postive = go.Scatter(x=X_postive, y=Y_postive, mode='markers+lines', name='postive')
trace_negative = go.Scatter(x=X_negative, y=Y_negative, mode='markers+lines', name='negative')
trace_neutral = go.Scatter(x=X_neutral, y=Y_neutral, mode='markers+lines', name='neutral')

data = [trace_postive, trace_negative, trace_neutral]

layout = go.Layout(title='Sentiment Static Data Test')
fig = go.Figure(data=data, layout=layout)
pyo.plot(fig)


# 		X = df.equip_id.values[-100:]
# 		Y = df.sentiment_smoothed.values[-100:]

# 		data = plotly.graph_objs.Scatter(
# 				x=list(X),
# 				y=list(Y),
# 				name='Scatter',
# 				mode='lines+makers'
# 			)

# 		return {'data': [data], 'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
# 													 yaxis=dict(range=[min(Y),max(Y)]),)}

# 	except Exception as e:
# 		with open('errors.txt', 'a') as f:
# 			f.write(str(e))
# 			f.write('\n')

# if __name__ == '__main__':
# 	app.run_server(debug=True)

