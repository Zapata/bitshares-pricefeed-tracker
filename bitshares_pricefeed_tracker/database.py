from sqlalchemy import create_engine
from sqlalchemy import Table, Column, DateTime, Float, Integer, String, Text, MetaData
from sqlalchemy.sql import select, func, text
import pandas as pd
import config

db = create_engine(config.DATABASE, echo=config.DEBUG)

metadata = MetaData()

prices = Table('prices', metadata,
     Column('timestamp', DateTime, nullable=False),
     Column('source', String, nullable=False),
     Column('tag', String),
     Column('blocknum', Integer),
     Column('publisher', String, nullable=False),
     Column('asset', String, nullable=False),
     Column('price', Float, nullable=False),
     Column('core_exchange_rate', Float),
     Column('maintenance_collateral_ratio', Integer),
     Column('maximum_short_squeeze_ratio', Integer),
     Column('details', Text)
)

metadata.create_all(db)
db.execute(text("select create_hypertable('prices', 'timestamp', if_not_exists => true, migrate_data => true)"))


def max_timestamp():
    return db.execute(select([func.max(prices.c.timestamp)])).scalar()

def min_timestamp():
    return db.execute(select([func.min(prices.c.timestamp)])).scalar()

def list_assets():
    query = select([prices.c.asset]).distinct().order_by(prices.c.asset)
    rows = db.execute(query).fetchall()
    return [ c for (c, ) in rows ]

def list_publishers(asset):
    query = select([prices.c.publisher]).where(prices.c.asset == asset).distinct().order_by(prices.c.publisher)
    rows = db.execute(query).fetchall()
    return [ c for (c, ) in rows ]

def get_prices(searched_asset=None, searched_publishers=None, start_date=None, end_date=None, searched_source='blockchain', searched_tag='mainnet'):
    print('get_prices({}, {}, {}, {})'.format(searched_asset, searched_publishers, start_date, end_date))
    query = select([prices.c.publisher, prices.c.timestamp, prices.c.price])
    query = query.order_by(prices.c.publisher, prices.c.timestamp)
    if searched_asset:
        query = query.where(prices.c.asset == searched_asset)
    if searched_publishers:
        query = query.where(prices.c.publisher.in_(searched_publishers))
    if searched_source:
        query = query.where(prices.c.source == searched_source)
    if searched_tag:
        query = query.where(prices.c.tag == searched_tag)
    if start_date:
        query = query.where(prices.c.timestamp >= start_date)
    if end_date:
        query = query.where(prices.c.timestamp <= end_date)
                
    return pd.read_sql(query, db)

def get_medians(searched_asset=None, start_date=None, end_date=None, searched_source='blockchain', searched_tag='mainnet'):
    print('get_median({}, {}, {})'.format(searched_asset, start_date, end_date))
    df = get_prices(searched_asset=searched_asset, start_date=start_date, end_date=end_date, searched_source=searched_source, searched_tag=searched_tag)
    all_dates = df['timestamp'].drop_duplicates()
    medians = pd.DataFrame()
    for name, group in df.groupby('publisher'):
        group = group.drop('publisher', axis=1)
        group = group.drop_duplicates(subset='timestamp')
        group = group.set_index('timestamp')
        group = group.reindex(all_dates, method='ffill')
        medians = medians.append(group)
    medians = medians.groupby('timestamp').median()
    return medians.reset_index()