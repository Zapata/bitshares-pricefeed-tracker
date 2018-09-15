import schedule
import time
import threading
from bitshares_pricefeed_monitor.loader import load_recent_pricefeeds, load_historic_pricefeeds


load_recent_pricefeeds()

historic_loader_thread = threading.Thread(target=load_historic_pricefeeds)
historic_loader_thread.start()

schedule.every(1).minutes.do(load_recent_pricefeeds)

while True:
    schedule.run_pending()
    time.sleep(1)