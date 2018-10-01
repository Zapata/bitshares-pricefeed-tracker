# Bitshares Pricefeed Monitor

Install virtual environment and setup:

    pip install virtualenv
    virtualenv -p python3 wrappers_env/
    source wrappers_env/bin/activate

Install dependencies:

    pip install -r requirements.pip

To run you will need:

  - a connection to a [Timescale Database](https://www.timescale.com/), configured using `DATABASE` environment variable. If the database is empty, the tables will be created at first run.
  - a connection to a Elastic Search cluster populated with Bitshares blockchain data. Configure it using `ELASTICSEARCH_URL`, `ELASTICSEARCH_USER` and `ELASTICSEARCH_PASSWORD` environment variables.
  - a connection to a Bitshares API node, configured using `BITSHARES_WEBSOCKET_NODE` environment variables.

Then:

  - to load all the pricefeed data in TimescaleDB: `python loader.py`
  - to serve the web interface: `python web.py`
