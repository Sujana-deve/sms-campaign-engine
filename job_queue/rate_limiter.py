#this file sets the rate limit for the queeue.
import time
from config.settings import SMS_RATE_LIMIT

class RateLimiter:
    def __init__(self,rate = SMS_RATE_LIMIT):
        self.rate = rate
        self.delay = 1.0/rate
    
    def wait(self):
        time.sleep(self.delay)
        print(f"rate limiter:waiting {self.delay}s before next job")
