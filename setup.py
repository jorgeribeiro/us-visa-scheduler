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
        else:
            break

def lambda_handler(event, context):
    handler = VisaScheduler()
    result = handler.main()
    
    # Determine the next execution time based on the result
    next_execution_time = calculate_next_execution_time(result)

    # Update the EventBridge rule schedule dynamically
    update_eventbridge_rule_schedule(next_execution_time)

def calculate_next_execution_time(result):
    import datetime

    default_next_execution_time = datetime.datetime.now() + datetime.timedelta(seconds=Time.SUCCESS_TIME)
    if result == Result.RETRY:
        return datetime.datetime.now() + datetime.timedelta(seconds=Time.RETRY_TIME)
    elif result == Result.COOLDOWN:
        return datetime.datetime.now() + datetime.timedelta(seconds=Time.COOLDOWN_TIME)
    elif result == Result.EXCEPTION:
        return datetime.datetime.now() + datetime.timedelta(seconds=Time.EXCEPTION_TIME)
    elif result == Result.WEBDRIVER_EXCEPTION:
        return datetime.datetime.now() + datetime.timedelta(seconds=Time.WEBDRIVER_EXCEPTION_TIME)
    elif result == Result.SUCCESS:
        return datetime.datetime.now() + datetime.timedelta(seconds=Time.SUCCESS_TIME)
    
    return default_next_execution_time

def update_eventbridge_rule_schedule(next_execution_time):
    import boto3

    # Update the EventBridge rule schedule using AWS SDK
    client = boto3.client('events')
    rule_name = 'elizabethSlotSearchEventBridgeRule'

    client.put_rule(
        Name=rule_name,
        ScheduleExpression=f'cron({next_execution_time.minute} {next_execution_time.hour} {next_execution_time.day} {next_execution_time.month} ? {next_execution_time.year})',
        State='ENABLED'
    )