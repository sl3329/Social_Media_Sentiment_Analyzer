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

conn = psycopg2.connect(host='ec2-54-243-112-184.compute-1.amazonaws.com', database='tweetsdata', user='shan', password='password')
c = conn.cursor()

df = pd.read_sql("SELECT * FROM word_sentiment LIMIT 1000000", conn)

# df_positive = pd.read_sql("SELECT tag, count(count) FROM tag_sentiment WHERE sentiment = 'positive' GROUP BY tag LIMIT 20", conn)
# # df_positive.sort_values('equip_id', inplace=True)

# # df_negative = pd.read_sql("SELECT * FROM tag_sentiment WHERE sentiment = 'negative' ORDER BY equip_id DESC LIMIT 20", conn)
# # df_negative.sort_values('equip_id', inplace=True)

# # df_neutral = pd.read_sql("SELECT * FROM tag_sentiment WHERE sentiment = 'neutral' ORDER BY equip_id DESC LIMIT 20", conn)
# # df_neutral.sort_values('equip_id', inplace=True)
# print(df)
# print(df_positive)

app = dash.Dash()
app.layout = html.Div([
			dcc.Graph(id='graph'),
			dcc.Input(id='my-id', value='Initial Text', type='text'),
			html.Div(id='my-div')
])

@app.callback(Output('graph', 'figure'),
			[Input(component_id='my-id', component_property='value')])
def update_figure(input_value):

	filtered_df = df[df['word'] == input_value]

	traces = []

	for sentiment_status in filtered_df['sentiment'].unique():
		df_by_sentiment = filtered_df[filtered_df['sentiment']==sentiment_status]
		traces.append(go.Scatter(
				x = df_by_sentiment['timestamp'],
				y = df_by_sentiment['count'],
				mode = 'markers+lines',
				name = sentiment_status
			))

	return {'data':traces,
			'layout':go.Layout(title='My Plot')}

if __name__ == '__main__':
	app.run_server()