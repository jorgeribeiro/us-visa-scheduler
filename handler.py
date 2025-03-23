import logging
import boto3

from utils import Time
from visa import VisaScheduler, Result

logger = logging.getLogger("Visa_Logger")

def lambda_handler(event, context):
    handler = VisaScheduler()
    result = handler.main()
    logger.info(f'Lambda function executed with result: {result}')

    next_rate = f"{Time.RETRY_TIME // 60} minutes"
    disable_schedule = False
    if result == Result.RETRY:
        next_rate = f"{Time.RETRY_TIME // 60} minutes"
    elif result == Result.COOLDOWN:
        next_rate = f"{Time.COOLDOWN_TIME // 60} minutes"
    elif result == Result.EXCEPTION:
        next_rate = f"{Time.EXCEPTION_TIME // 60} minutes"
    elif result == Result.WEBDRIVER_EXCEPTION:
        next_rate = f"{Time.WEBDRIVER_EXCEPTION_TIME // 60} minutes"
    elif result == Result.FAILED_RESCHEDULE:
        next_rate = f"{Time.FAILED_RESCHEDULE_TIME // 60} minutes"
    elif result == Result.SUCCESSFUL_RESCHEDULE or result == Result.EARLIER_SLOT_FOUND:
        next_rate = "7 days"
    elif result == Result.STOP:
        disable_schedule = True

    logger.info(f"Next rate: {next_rate}, Disable schedule: {disable_schedule}")
    event_arn = event["resources"][0]
    event_arn = event_arn[event_arn.rindex("/") + 1:]
    scheduler_client = boto3.client('scheduler')
    schedule = scheduler_client.get_schedule(Name=event_arn)
    scheduler_client.update_schedule(
        FlexibleTimeWindow=schedule["FlexibleTimeWindow"],
        Name=event_arn,
        ScheduleExpression=f"rate({next_rate})",
        Target=schedule["Target"],
        ScheduleExpressionTimezone=schedule["ScheduleExpressionTimezone"],
        State="DISABLED" if disable_schedule else "ENABLED"
    )