import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import plotly.graph_objs as go

import bitshares_pricefeed_monitor.database as db
from sqlalchemy.sql import select, and_


app = dash.Dash()

def build_layout():
    min_date = db.min_timestamp().isoformat()
    max_date = db.max_timestamp().isoformat()
    return html.Div([
        html.H1(children='BitShares Feed Tracker', style={'text-align': 'center'}),
        html.Div(className='pure-g', children=[
            html.Div(className='pure-u-1-5', children=[
                html.Form(className="pure-form-stacked", children=[
                    html.Fieldset(children=[
                        html.Label('Asset:'),
                        dcc.Dropdown(
                            id='asset-dropdown',
                            options=[{'label': asset, 'value': asset} for asset in db.list_assets()],
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
                        html.Label(children='From:'),
                        dcc.Input(id='from-date', type='datetime-local', min=min_date, max=max_date, value=min_date),
                        html.Label(children='To:'),
                        dcc.Input(id='to-date', type='datetime-local', min=min_date, max=max_date, value=None),
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
        return db.list_publishers(selected_asset)
    else:
        return []


@app.callback(Output('publisher-dropdown', 'options'), [Input('asset-dropdown', 'value')])
def set_publisher_options(selected_asset):
    publishers = db.list_publishers(selected_asset)
    return [{'label': p, 'value': p} for p in publishers]


@app.callback(
    Output('price-graph', 'figure'), 
    [ 
        Input('asset-dropdown', 'value'),
        Input('publisher-dropdown', 'value'),
        Input('from-date', 'value'),
        Input('to-date', 'value'),
        Input('options', 'values'),
    ])
def update_graph(selected_asset, selected_publishers, start_date, end_date, options):
    if not (selected_asset and selected_publishers):
        return {}

    df = db.get_prices(searched_asset=selected_asset, searched_publishers=selected_publishers, start_date=start_date, end_date=end_date)

    data = [ 
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

    if 'median' in options:
        median = db.get_medians(searched_asset=selected_asset, start_date=start_date, end_date=end_date)
        data.append(go.Scatter(
            x= median.timestamp,
            y= median.price,
            name= 'median',
            mode= 'lines+markers',
            line=dict(
                shape='hv'
            )
        ))
    
    return { 'data': data }

external_css = [
    "https://unpkg.com/purecss@1.0.0/build/base-min.css",
    "https://unpkg.com/purecss@1.0.0/build/pure-min.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    import config
    app.run_server(debug=config.DEBUG)
