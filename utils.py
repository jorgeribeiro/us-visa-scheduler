from enum import Enum
import random

class Time:
    RETRY_TIME = random.choice([60 * 27, 60 * 34, 60 * 37])  # wait time when retrying: 27, 34 or 37 minutes
    COOLDOWN_TIME = random.choice([60 * 123, 60 * 128, 60 * 131])  # wait time when temporarily banned (empty list): 123, 128 or 131 minutes
    EXCEPTION_TIME = random.choice([60 * 6, 60 * 9, 60 * 13])  # wait time when an exception occurs: 6, 9 or 13 minutes
    WEBDRIVER_EXCEPTION_TIME = 60  # wait time when webdriver exception occurs: 1 minute
    SUCCESS_TIME = 60 * 60 * 24 * 7  # wait time when successfully rescheduled: 7 days

class Result(Enum):
    SUCCESS = 1
    RETRY = 2
    COOLDOWN = 3
    EXCEPTION = 4
    WEBDRIVER_EXCEPTION = 5
    STOP = 6
