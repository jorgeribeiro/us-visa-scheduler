import logging
import boto3

from utils import Time
from visa import VisaScheduler, Result

logger = logging.getLogger("Visa_Logger")

def lambda_handler(event, context):
    handler = VisaScheduler()
    result = handler.main()
    logger.info(f'Lambda function executed with result: {result}')
    
    next_rate = Time.RETRY_TIME
    disable_schedule = False
    if result == Result.RETRY:
        next_rate = Time.RETRY_TIME
    elif result == Result.COOLDOWN:
        next_rate = Time.COOLDOWN_TIME
    elif result == Result.EXCEPTION:
        next_rate = Time.EXCEPTION_TIME
    elif result == Result.WEBDRIVER_EXCEPTION:
        next_rate = Time.WEBDRIVER_EXCEPTION_TIME
    elif result == Result.SUCCESS:
        next_rate = Time.SUCCESS_TIME
    elif result == Result.STOP:
        disable_schedule = True
    
    event_arn = event["resources"][0]
    event_arn = event_arn[event_arn.rindex("/") + 1:]
    scheduler_client = boto3.client('scheduler')
    schedule = scheduler_client.get_schedule(Name=event_arn)
    scheduler_client.update_schedule(
        FlexibleTimeWindow=schedule["FlexibleTimeWindow"], 
        Name=event_arn, 
        ScheduleExpression=f"rate({next_rate // 60} minutes)", 
        Target=schedule["Target"], 
        State="DISABLED" if disable_schedule else "ENABLED"
    )