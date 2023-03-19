#!/usr/bin/env python

from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import requests
from datetime import datetime
import pandas_ta as ta

def fetch_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/ohlc?vs_currency=usd&days=30&interval=daily"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def add_moving_average(df, window=20):
    df['MA'] = df['close'].rolling(window=window).mean()
    return df

def add_bollinger_bands(df, window=10, num_std=1.5):
    bbands = ta.bbands(df['close'], length=window, stddev=num_std)
    df['BB_High'] = bbands.iloc[:, 0]
    df['BB_Mid'] = bbands.iloc[:, 1]
    df['BB_Low'] = bbands.iloc[:, 2]
    return df

app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='candlestick_chart', style={'width': '100vw', 'height': '100vh'}),
    dcc.Interval(id='interval_component', interval=3600 * 1000 * 30, n_intervals=0),
])

@app.callback(Output('candlestick_chart', 'figure'), Input('interval_component', 'n_intervals'))
def update_candlestick_chart(n):
    df = fetch_data()
    df = add_moving_average(df)
    df = add_bollinger_bands(df)

    trace = go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='BTC/USD'
    )

    ma_trace = go.Scatter(
        x=df['timestamp'],
        y=df['MA'],
        mode='lines',
        line=dict(color='orange'),
        name='Moving Average (20)'
    )

    bollinger_high_trace = go.Scatter(
        x=df['timestamp'],
        y=df['BB_High'],
        mode='lines',
        line=dict(color='blue', width=1),
        name='Bollinger Bands High',
    )

    bollinger_mid_trace = go.Scatter(
        x=df['timestamp'],
        y=df['BB_Mid'],
        mode='lines',
        line=dict(color='blue', width=1, dash='dash'),
        name='Bollinger Bands Mid',
    )

    bollinger_low_trace = go.Scatter(
        x=df['timestamp'],
        y=df['BB_Low'],
        mode='lines',
        line=dict(color='blue', width=1),
        name='Bollinger Bands Low',
    )

    layout = go.Layout(
        title='Bitcoin Price',
        yaxis_title='Price (USD)',
        xaxis=dict(type='date', tick0=df['timestamp'][0], dtick='M1'),
        legend=dict(orientation='h', y=-0.3)
    )

    return {'data': [trace, ma_trace, bollinger_low_trace, bollinger_mid_trace, bollinger_high_trace], 'layout': layout}

if __name__ == '__main__':
    app.run_server(debug=True)
