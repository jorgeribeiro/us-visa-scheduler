from datetime import datetime, time
from enum import Enum
import random

class Time:
    RETRY_TIME = random.choice([60 * 7, 60 * 8, 60 * 10])  # wait time when retrying: 7, 8 or 10 minutes
    COOLDOWN_TIME = random.choice([60 * 123, 60 * 128, 60 * 131])  # wait time when temporarily banned (empty list): 123, 128 or 131 minutes
    EXCEPTION_TIME = random.choice([60 * 47, 60 * 52, 60 * 64])  # wait time when an exception occurs: 47, 52 or 64 minutes
    WEBDRIVER_EXCEPTION_TIME = 60  # wait time when webdriver exception occurs: 1 minute
    FAILED_RESCHEDULE_TIME = 60  # wait time when failed to reschedule: 1 minute

# Peak windows (weekday-only) during which RETRY / WEBDRIVER_EXCEPTION / FAILED_RESCHEDULE
# next-runs are scheduled every PEAK_INTERVAL_CHOICES minutes.
# Evaluated in the timezone configured via os.environ['TZ'] (set in VisaScheduler.__init__).
PEAK_WINDOWS = [
    (time(7, 30), time(10, 30)),
    (time(18, 0), time(21, 0)),
]
PEAK_INTERVAL_CHOICES = [2, 3, 4, 5]

def is_peak_now():
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    current = now.time()
    return any(start <= current < end for start, end in PEAK_WINDOWS)

def peak_interval_minutes():
    return random.choice(PEAK_INTERVAL_CHOICES)

class Result(Enum):
    SUCCESSFUL_RESCHEDULE = 'Successful reschedule'
    EARLIER_SLOT_FOUND = 'Earlier slot found'
    FAILED_RESCHEDULE = 'Failed reschedule'
    RETRY = 'Retry'
    COOLDOWN = 'Cooldown'
    EXCEPTION = 'Exception'
    WEBDRIVER_EXCEPTION = 'Webdriver exception'
    STOP = 'Stop'
