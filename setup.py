import time

from utils import Time
from visa import VisaScheduler, Result

def as_loop():
    while 1:
        handler = VisaScheduler()
        result = handler.main()
        
        if result == Result.RETRY:
            time.sleep(Time.RETRY_TIME)
        elif result == Result.COOLDOWN:
            time.sleep(Time.COOLDOWN_TIME)
        elif result == Result.EXCEPTION:
            time.sleep(Time.EXCEPTION_TIME)
        elif result == Result.WEBDRIVER_EXCEPTION:
            time.sleep(Time.WEBDRIVER_EXCEPTION_TIME)
        elif result == Result.FAILED_RESCHEDULE:
            time.sleep(Time.FAILED_RESCHEDULE_TIME)
        else:
            break