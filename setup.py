import time
import datetime
import boto3

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
        else:
            break

def lambda_handler(event, context):
    handler = VisaScheduler()
    result = handler.main()
    
    next_execution_time, disable_rule = calculate_next_execution_time(result)
    if not disable_rule:
        update_eventbridge_rule_schedule(next_execution_time)
    else:
        disable_eventbridge_rule()

def calculate_next_execution_time(result):
    default_next_execution_time = datetime.datetime.now() + datetime.timedelta(seconds=Time.SUCCESS_TIME), False
    if result == Result.RETRY:
        return datetime.datetime.now() + datetime.timedelta(seconds=Time.RETRY_TIME), False
    elif result == Result.COOLDOWN:
        return datetime.datetime.now() + datetime.timedelta(seconds=Time.COOLDOWN_TIME), False
    elif result == Result.EXCEPTION:
        return datetime.datetime.now() + datetime.timedelta(seconds=Time.EXCEPTION_TIME), False
    elif result == Result.WEBDRIVER_EXCEPTION:
        return datetime.datetime.now() + datetime.timedelta(seconds=Time.WEBDRIVER_EXCEPTION_TIME), False
    elif result == Result.SUCCESS:
        return datetime.datetime.now() + datetime.timedelta(seconds=Time.SUCCESS_TIME), True
    elif result == Result.STOP:
        return None, True
    
    return default_next_execution_time

def update_eventbridge_rule_schedule(next_execution_time):
    client = boto3.client('events')
    rule_name = 'elizabethSlotSearchEventBridgeRule'

    client.put_rule(
        Name=rule_name,
        ScheduleExpression=f'cron({next_execution_time.minute} {next_execution_time.hour} {next_execution_time.day} {next_execution_time.month} ? {next_execution_time.year})',
        State='ENABLED'
    )

def disable_eventbridge_rule():
    client = boto3.client('events')
    rule_name = 'elizabethSlotSearchEventBridgeRule'

    client.disable_rule(
        Name=rule_name
    )