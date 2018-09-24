from sqlalchemy import create_engine
from sqlalchemy import Table, Column, DateTime, Float, Integer, String, Text, MetaData
from sqlalchemy.sql import select, func, text
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
db.execute(text("select create_hypertable('prices', 'timestamp', if_not_exists => true)"))


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

