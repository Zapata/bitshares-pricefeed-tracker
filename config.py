from dateutil import parser

# Since how far in time should we load the pricefeed in the database?
OLDEST_PRICEFEED_DATETIME = parser.parse('2018-09-13')

BITSHARES_WEBSOCKET_NODE = 'wss://api.dex.trading'
BITSHARES_ELASTIC_SEARCH_NODE = {
    'hosts': ['https://elasticsearch.bitshares.ws/'], 
    'http_auth': ('BitShares', 'Infrastructure')
}

# DATABASE = 'postgres://postgres:secret@localhost:5432/postgres'
DATABASE = 'sqlite:///:memory:'
DEBUG = False