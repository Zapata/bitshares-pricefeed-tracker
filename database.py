from sqlalchemy import create_engine
from sqlalchemy import Table, Column, DateTime, Float, Integer, String, Text, MetaData
from sqlalchemy.sql import select, func

#db = create_engine('postgres://postgres:secret@localhost:5432/postgres', echo=True)
db = create_engine('sqlite:///:memory:', echo=True)

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

def max_timestamp():
    return db.execute(select([func.max(prices.c.timestamp)])).scalar()

def min_timestamp():
    return db.execute(select([func.min(prices.c.timestamp)])).scalar()