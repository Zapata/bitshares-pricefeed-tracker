import pandas as pd
from datetime import datetime
from .loader import get_market_history

def get_dex_prices(asset, start_date, end_date):
    if not end_date:
        end_date = datetime.utcnow().replace(microsecond=0).isoformat()
    h = get_market_history(asset, start_date, end_date)
    df = pd.DataFrame(h)
    return df