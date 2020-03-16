from dateutil import parser
import os

# Since how far in time should we load the pricefeed in the database?
OLDEST_PRICEFEED_DATETIME = parser.parse(os.environ.get('OLDEST_PRICEFEED_DATETIME', '2018-09-14'))
MAX_DATE_RANGE_IN_DAYS = int(os.environ.get('MAX_DATE_RANGE_IN_DAYS', '3'))

BITSHARES_WEBSOCKET_NODE = os.environ.get('WEBSOCKET_URL', 'ws://localhost:8090/ws')
BITSHARES_ELASTIC_SEARCH_NODE = {
    'hosts': os.environ.get('ELASTICSEARCH_URL', 'http://localhost/').split(','), 
    'http_auth': (
        os.environ.get('ELASTICSEARCH_USER', 'BitShares'), 
        os.environ.get('ELASTICSEARCH_PASSWORD', '******')
    ),
    'timeout': int(os.environ.get('ELASTICSEARCH_TIMEOUT', '10'))
}

DATABASE = os.environ.get('DATABASE', 'postgres://postgres:secret@localhost:5432/postgres')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'