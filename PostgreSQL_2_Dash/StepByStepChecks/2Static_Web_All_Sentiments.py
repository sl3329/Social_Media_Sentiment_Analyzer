import pandas as pd
import psycopg2
import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import pandas as pd
import plotly.offline as pyo

app = dash.Dash()

app.layout = html.Div(
    html.Div([
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000*2, # in milliseconds
            n_intervals=0
        )
    ])
)


@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])

def update_graph(n):
	try:
		conn = psycopg2.connect(host='ec2-54-243-112-184.compute-1.amazonaws.com', database='tweetsdata', user='shan', password='password')
		c = conn.cursor()

		df_positive = pd.read_sql("SELECT * FROM sentiment WHERE sentiment = 'positive' ORDER BY equip_id DESC LIMIT 50", conn)
		df_positive.sort_values('equip_id', inplace=True)

		df_negative = pd.read_sql("SELECT * FROM sentiment WHERE sentiment = 'negative' ORDER BY equip_id DESC LIMIT 50", conn)
		df_negative.sort_values('equip_id', inplace=True)

		df_neutral = pd.read_sql("SELECT * FROM sentiment WHERE sentiment = 'neutral' ORDER BY equip_id DESC LIMIT 50", conn)
		df_neutral.sort_values('equip_id', inplace=True)

		# df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
		print(df_positive)
		print(df_negative)

		X_positive = df_positive['timestamp']
		Y_positive = df_positive['count']
		X_negative = df_negative['timestamp']
		Y_negative = df_negative['count']
		X_neutral = df_neutral['timestamp']
		Y_neutral = df_neutral['count']

		data = plotly.graph_objs.Scatter(
				x=X_positive,
				y=Y_positive,
				name='Scatter',
				mode='markers+lines'
				)

		return {'data':[data],'layout':go.Layout(xaxis=dict(range=[min(X_positive),max(X_positive)]),
												yaxis=dict(range=[min(Y_positive),max(Y_positive)]),)}

	# 	trace_positive = go.Scatter(x=X_positive, y=Y_positive, mode='markers+lines', name='positive', marker={'color':'#faafc0'})
	# 	trace_negative = go.Scatter(x=X_negative, y=Y_negative, mode='markers+lines', name='negative', marker={'color':'#f2faaf'})
	# 	trace_neutral = go.Scatter(x=X_neutral, y=Y_neutral, mode='markers+lines', name='neutral', marker={'color':'#70deff'})

	# 	data = [trace_positive, trace_negative, trace_neutral]

	# 	layout = go.Layout(title='Sentiment Static Data Test')
	# 	fig = go.Figure(data=data, layout=layout)
	# 	pyo.plot(fig)

	# 	fig = go.Figure(data=[
	# 					go.Scatter(x=X_positive, y=Y_positive, mode='markers+lines', name='positive', marker={'color':'#faafc0'})
	# 		])
	# 	return fig

	except Exception as e:
		with open('errors.txt', 'a') as f:
			f.write(str(e))
			f.write('\n')

if __name__ == '__main__':
	app.run_server(debug=True)

