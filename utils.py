from enum import Enum
import random

class Time:
    RETRY_TIME = random.choice([60 * 20, 60 * 24, 60 * 30])  # wait time when retrying: 20, 24 or 30 minutes
    COOLDOWN_TIME = random.choice([60 * 123, 60 * 128, 60 * 131])  # wait time when temporarily banned (empty list): 123, 128 or 131 minutes
    EXCEPTION_TIME = random.choice([60 * 47, 60 * 52, 60 * 64])  # wait time when an exception occurs: 47, 52 or 64 minutes
    WEBDRIVER_EXCEPTION_TIME = 60  # wait time when webdriver exception occurs: 1 minute
    FAILED_RESCHEDULE_TIME = 60  # wait time when failed to reschedule: 1 minute

class Result(Enum):
    SUCCESSFUL_RESCHEDULE = 'Successful reschedule'
    EARLIER_SLOT_FOUND = 'Earlier slot found'
    FAILED_RESCHEDULE = 'Failed reschedule'
    RETRY = 'Retry'
    COOLDOWN = 'Cooldown'
    EXCEPTION = 'Exception'
    WEBDRIVER_EXCEPTION = 'Webdriver exception'
    STOP = 'Stop'
