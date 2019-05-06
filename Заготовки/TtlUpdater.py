import threading
import time
from DnsServerCache import DNSServerCache


class TTLUpdater(threading.Thread):
    def __init__(self, cache: DNSServerCache):
        threading.Thread.__init__(self)
        self.cache = cache

    def run(self):
        while True:
            self.cache.update_ttl(1)
            time.sleep(1000)
