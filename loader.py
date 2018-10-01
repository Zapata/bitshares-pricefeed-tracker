import schedule
import time
import threading
from bitshares_pricefeed_monitor.loader import load_recent_pricefeeds, load_historic_pricefeeds
import functools

def safely_load_historic_pricefeeds():
    while True:
        try:
            return load_historic_pricefeeds()
        except:
            import traceback
            print(traceback.format_exc())
            time.sleep(10)

def safely_load_recent_pricefeeds():
    try:
        load_recent_pricefeeds()
    except:
        import traceback
        print(traceback.format_exc())

load_recent_pricefeeds()

historic_loader_thread = threading.Thread(target=safely_load_historic_pricefeeds)
historic_loader_thread.start()

schedule.every(1).minute.do(safely_load_recent_pricefeeds)

while True:
    schedule.run_pending()
    time.sleep(1)