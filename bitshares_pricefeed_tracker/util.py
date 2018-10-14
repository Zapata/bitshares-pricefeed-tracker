import requests
import pandas as pd
from datetime import datetime
import dateutil.parser
from .loader import get_market_history

def get_dex_prices(asset, start_date, end_date):
    if not end_date:
        end_date = datetime.utcnow().replace(microsecond=0).isoformat()
    h = get_market_history(asset, start_date, end_date)
    df = pd.DataFrame(data=h, columns=['timestamp', 'open', 'close', 'low', 'high'])
    return df

_request_headers = {'content-type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

_cex_pairs = {
    'USD': 'bts_usdt',
    'CNY': 'bts_qc'
}

_zb_buckets = [
    (  60,  '1min' ),
    ( 180,  '3min' ),
    ( 300,  '5min' ),
    ( 900, '15min' ),
    ( 1800, '30min' ),
    ( 3600, '1hour'),
    ( 7200, '2HOUR'),
    ( 14400, '4hour'),
    ( 21600, '6hour'),
    ( 43200, '12hour'),
    ( 86400, '1day'),
    ( 259200, '3day'),
    ( 604800, '1week')
]

_zb_max_returned_elements = 200

def _compute_zb_bucket_size(start_date):
    date_range = datetime.utcnow() - dateutil.parser.parse('{} UTC'.format(start_date)).replace(tzinfo=None)
    return next( (bucket[1] for bucket in _zb_buckets if date_range.total_seconds() / bucket[0] < _zb_max_returned_elements), _zb_buckets[-1][1])

def has_cex_prices(asset):
    return bool(asset in _cex_pairs)

def cex_price_source(asset):
    return 'ZB {}'.format(_cex_pairs[asset]).upper().replace('_', '/')

def get_cex_prices(asset, start_date):
    start_timestamp = int(dateutil.parser.parse('{} UTC'.format(start_date)).timestamp() * 1e3)
    bucket = _compute_zb_bucket_size(start_date)
    url = 'http://api.zb.cn/data/v1/kline?market={}&type={}&since={}'.format(_cex_pairs[asset], bucket, start_timestamp)
    response = requests.get(
        url=url,
        headers=_request_headers,
        timeout=5).json()
    if 'data' not in response:
        return None
    df = pd.DataFrame(response['data'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df.timestamp = df.timestamp.map(lambda d : datetime.utcfromtimestamp(d / 1e3).isoformat())
    return df