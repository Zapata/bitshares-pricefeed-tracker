import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from pandas_datareader import data as web
from datetime import datetime as dt

import pandas as pd
from bitshares_pricefeed_monitor.database import db, prices, list_assets, list_publishers
from sqlalchemy.sql import select, and_


app = dash.Dash()

def build_layout():
    return html.Div([
        html.H1('Bitshares Feed Tracker'),
        html.Div([
            dcc.Dropdown(
                id='asset-dropdown',
                options=[{'label': asset, 'value': asset} for asset in list_assets()],
                value='CNY'
            ),
            dcc.Dropdown(id='publisher-dropdown', multi=True,)
        ]),
        dcc.Graph(id='price-graph')
    ])

app.layout = build_layout()


@app.callback(Output('publisher-dropdown', 'options'), [Input('asset-dropdown', 'value')])
def set_publisher_options(selected_asset):
    publishers = list_publishers(selected_asset)
    return [{'label': p, 'value': p} for p in publishers]


@app.callback(
    Output('price-graph', 'figure'), 
    [ 
        Input('asset-dropdown', 'value'),
        Input('publisher-dropdown', 'value'),
    ])
def update_graph(selected_asset, selected_publishers):
    query = select([prices.c.publisher, prices.c.timestamp, prices.c.price]).\
                where(
                    and_(
                        prices.c.publisher.in_(selected_publishers), 
                        prices.c.asset == selected_asset
                    )
                ).\
                order_by(prices.c.publisher, prices.c.timestamp)
    df = pd.read_sql(query, db)

    return {
        'data': [{
            'x': df[df['publisher'] == publisher].timestamp,
            'y': df[df['publisher'] == publisher].price,
            'name': publisher
        } for publisher in df.publisher.unique()
        ]
    }

if __name__ == '__main__':
    app.run_server()
