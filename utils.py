from enum import Enum

class Time:
    RETRY_TIME = 60 * 10 # wait time when retrying: 10 minutes
    COOLDOWN_TIME = 60 * 60  # wait time when temporary banned (empty list): 60 minutes
    EXCEPTION_TIME = 60 * 5  # wait time when an exception occurs: 5 minutes
    WEBDRIVER_EXCEPTION_TIME = 60  # wait time when webdriver exception occurs: 1 minute
    SUCCESS_TIME = 60 * 60 * 24 * 7  # wait time when success: 7 days

class Result(Enum):
    SUCCESS = 1
    RETRY = 2
    COOLDOWN = 3
    EXCEPTION = 4
    WEBDRIVER_EXCEPTION = 5
    STOP = 6
