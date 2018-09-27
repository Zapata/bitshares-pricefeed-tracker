import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import plotly.graph_objs as go

import pandas as pd
from bitshares_pricefeed_monitor.database import db, prices, list_assets, list_publishers, min_timestamp, max_timestamp
from sqlalchemy.sql import select, and_


app = dash.Dash()

def build_layout():
    return html.Div([
        html.H1(children='BitShares Feed Tracker', style={'text-align': 'center'}),
        html.Div(className='pure-g', children=[
            html.Div(className='pure-u-1-5', children=[
                html.Form(className="pure-form-stacked", children=[
                    html.Fieldset(children=[
                        html.Label('Asset:'),
                        dcc.Dropdown(
                            id='asset-dropdown',
                            options=[{'label': asset, 'value': asset} for asset in list_assets()],
                            value='CNY'
                        ),
                        html.Label(children='Publishers:'),
                        dcc.Dropdown(id='publisher-dropdown', multi=True),
                        dcc.Checklist(
                            id='publisher-option',
                            options=[
                                {'label': 'All', 'value': 'publishers-all'}
                            ],
                            labelClassName='pure-checkbox',
                            labelStyle={'text-align': 'right'},
                            values=[]
                        ),
                        html.Label(children='Date range:'),
                        dcc.DatePickerRange(
                            id='date-picker-range',
                            min_date_allowed=min_timestamp(),
                            max_date_allowed=max_timestamp(),
                            start_date=min_timestamp(),
                            end_date_placeholder_text='Select a date!'
                        ),
                        html.Label(children='Additional feeds:'),
                        dcc.Checklist(
                            id='options',
                            options=[
                                {'label': 'Feed median', 'value': 'median'},
                                {'label': 'DEX price', 'value': 'internal'},
                                {'label': 'External price', 'value': 'external'}
                            ],
                            labelClassName='pure-checkbox',
                            values=[]
                        ),
                    ])
                ])
            ]),
            html.Div(className='pure-u-4-5', children=[
                dcc.Graph(id='price-graph')
            ])
        ])
    ])

app.layout = build_layout()


@app.callback(
    Output('publisher-dropdown', 'value'), 
    [
        Input('asset-dropdown', 'value'),
        Input('publisher-option', 'values')
    ])
def set_publisher_options(selected_asset, publisher_options):
    if 'publishers-all' in publisher_options:
        return list_publishers(selected_asset)
    else:
        return []


@app.callback(Output('publisher-dropdown', 'options'), [Input('asset-dropdown', 'value')])
def set_publisher_options(selected_asset):
    publishers = list_publishers(selected_asset)
    return [{'label': p, 'value': p} for p in publishers]


@app.callback(
    Output('price-graph', 'figure'), 
    [ 
        Input('asset-dropdown', 'value'),
        Input('publisher-dropdown', 'value'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
        Input('options', 'values'),
    ])
def update_graph(selected_asset, selected_publishers, start_date, end_date, options):
    if not (selected_asset and selected_publishers):
        return {}
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
        'data': [ 
            go.Scatter(
                x= df[df['publisher'] == publisher].timestamp,
                y= df[df['publisher'] == publisher].price,
                name= publisher,
                mode= 'lines+markers',
                line=dict(
                    shape='hv'
                )
            ) for publisher in df.publisher.unique()
        ]
    }

external_css = [
    "https://unpkg.com/purecss@1.0.0/build/base-min.css",
    "https://unpkg.com/purecss@1.0.0/build/pure-min.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    app.run_server(debug=True)
