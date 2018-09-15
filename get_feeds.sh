#! /bin/sh

curl -s --user BitShares:Infrastructure -X GET 'https://elasticsearch.bitshares.ws/bitshares-*/data/_search?pretty=true&size=1000' -H 'Content-Type: application/json' -d '
{
  "query": {
    "bool": {
      "filter": [
        {"term": {"operation_type": 19}}, 
        {"range": {
          "block_data.block_time": {"gte": "now-1d", "lte": "now"}
        }}
      ]
    }
  }
}
'