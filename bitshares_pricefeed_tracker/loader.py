from datetime import datetime, timedelta
from dateutil import parser
from elasticsearch_dsl import connections, Search, Q, A
import json
from .bitshares_websocket_client import client as bts
from .database import db, prices, max_timestamp, min_timestamp
import config

connections.create_connection(**config.BITSHARES_ELASTIC_SEARCH_NODE)

assets_by_id = {}
account_names_by_id = {}

def get_asset(asset_id):
    if asset_id not in assets_by_id:
        print('Load asset {}'.format(asset_id))
        asset = bts.get_object(asset_id)
        assets_by_id[asset_id] = { 'name': asset['symbol'], 'precision': 10 ** asset['precision'] }
    return assets_by_id[asset_id]

def get_asset_id(asset_name):
    return bts.request('database', 'lookup_asset_symbols', [[asset_name]])[0]['id']

def get_account_name(account_id):
    if account_id not in account_names_by_id:
        print('Load account {}'.format(account_id))
        account = bts.get_object(account_id)
        account_names_by_id[account_id] = account['name']
    return account_names_by_id[account_id]

def compute_price_inner(base_amount, base_precision, quote_amount, quote_precision, invert=False):
    price = (float(base_amount) / base_precision) / (float(quote_amount) / quote_precision) 
    return 1 / price if invert else price

def compute_price(price_data):
    quote_precision = get_asset(price_data['quote']['asset_id'])['precision']
    base_precision = get_asset(price_data['base']['asset_id'])['precision']
    return compute_price_inner(price_data['base']['amount'], base_precision, price_data['quote']['amount'], quote_precision)

def load_pricefeeds(from_date, to_date, batch_size=1000):
    count = 0
    s = Search(index="bitshares-*")
    s = s.extra(size=batch_size)
    s = s.query('bool', filter = [
            Q('term', operation_type=19),
            Q("range", block_data__block_time={'gte': from_date, 'lte': to_date})
        ])
    s = s.params(clear_scroll=False) # Avoid calling DELETE on ReadOnly apis.

    batch = []
    for hit in s.scan():
        count += 1
        op = json.loads(hit.operation_history.op)[1]
        batch.append({
            'timestamp': parser.parse(hit.block_data.block_time),
            'source': 'blockchain', # api, external
            'tag': 'mainnet',
            'blocknum': hit.block_data.block_num,
            'publisher': get_account_name(op['publisher']),
            'asset': get_asset(op['asset_id'])['name'],
            'price': compute_price(op['feed']['settlement_price']),
            'core_exchange_rate': compute_price(op['feed']['core_exchange_rate']),
            'maintenance_collateral_ratio': op['feed']['maintenance_collateral_ratio'],
            'maximum_short_squeeze_ratio': op['feed']['maximum_short_squeeze_ratio'],
            'details': '', # (json)
        })
        if (len(batch) == batch_size):
            db.execute(prices.insert(), batch)
            batch = []

    db.execute(prices.insert(), batch)
    return count

def load_recent_pricefeeds():
    start = max_timestamp()
    if not start:
        start =  (datetime.utcnow() - timedelta(hours=1))
    while start < datetime.utcnow():
        end = start + timedelta(hours=1)
        end_string = end.isoformat() if end < datetime.utcnow() else 'now'
        print("Load feeds from {} to {}.".format(start.isoformat(), end_string))
        count = load_pricefeeds(start.isoformat(), end_string)
        print("Loaded {} feeds from {} to {}.".format(count, start.isoformat(), end_string))
        start = end + timedelta(seconds=1)

def load_historic_pricefeeds():
    last = min_timestamp() - timedelta(seconds=1)
    while last > config.OLDEST_PRICEFEED_DATETIME:
        start = last - timedelta(hours=1)
        print("Load old feeds from {} to {}.".format(start.isoformat(), last.isoformat()))
        count = load_pricefeeds(start.isoformat(), last.isoformat())
        print("Loaded {} old feeds from {} to {}.".format(count, start.isoformat(), last.isoformat()))
        last = start - timedelta(seconds=1)

def get_market_history(asset, start, end):
    asset_id = get_asset_id(asset)
    # FIXME: Bucket size should be dynamically computed.
    # Currently bucket size is set to 900 as get_market_history returns only 200 elements.
    print('get_market_history({}, {}, {}, {}, {})'.format(asset_id, '1.3.0', 900, start, end))
    market_history = bts.request('history', 'get_market_history', [ asset_id, '1.3.0', 900, start, end ])
    if not market_history:
        return []
    base_precision = get_asset(market_history[0]['key']['base'])['precision']
    quote_precision = get_asset(market_history[0]['key']['quote'])['precision']
    invert = bool(market_history[0]['key']['base'] == '1.3.0')

    prices = [ {
        'timestamp': d['key']['open'],
        'open': compute_price_inner(d['open_base'], base_precision, d['open_quote'], quote_precision, invert=invert),
        'close': compute_price_inner(d['close_base'], base_precision, d['close_quote'], quote_precision, invert=invert),
        'low': compute_price_inner(d['low_base'], base_precision, d['low_quote'], quote_precision, invert=invert),
        'high': compute_price_inner(d['high_base'], base_precision, d['high_quote'], quote_precision, invert=invert),
    } for d in market_history ]
    return prices