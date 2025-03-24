# US Visa Scheduler

## How to run locally
- Install the required python packages: `pip install -r requirements.txt`
- Run `cp config.ini.example config.ini` and set the values correctly for the account you wish to run the scheduler
- Make sure the value of `['ENVIRONMENT']['USE']` in the `config.ini` is set to `LOCAL`
- Run `python -c "import setup; setup.as_loop()"`

## How to deploy as a Lambda function in AWS
- Run cp config.ini.example config.ini and set the values correctly for the account you wish to run the scheduler
- Make sure the value of `['ENVIRONMENT']['USE']` in the `config.ini` is set to `AWS`
- Run `deploy.sh` bash script with the arguments: `aws_account_id` (your AWS account ID), `username` (this is just a unique identifier for the image you are generating), `version` (a number that indicates the new version you are deploying), `region` (optional, if not informed value is set to `us-east-1`) and `profile` (indicates the AWS profile to be used, also optional, if not informed value is set to `default`)
- To successfully run the deployment script, the following must be correctly configured
    - Make sure the script is executable by running `chmod +x deploy.sh`
    - Docker daemon is running
    - AWS CLI is installed in your machine
    - AWS credentials are setup for the account ID you're using to deploy the image
    - If a Google Sheet is to be updated with the execution results (as explained in the section below) a `keyfile.json` must be present in the root directory
- For new Lambda functions, follow the steps below (only needed once for each Lambda function):
    - Create a new function (give it a descriptive and unique name) that is configured to run with a Container image. Considering that the image has already been deployed to an ECR repository, select it as the image for this function. Leave the Architecture as `x86_64`
    - After the function has been created successfuly, go to its Configuration and update the Timeout to 5 minutes and Memory to 2048 MB
    - Then, configure a new Schedule under Amazon EventBridge (give it a descriptive and unique name), and define its Schedule pattern as Recurring schedule > Rate-based schedule > 10 minutes as Rate expression. For Flexible time window, select `Off`
    - For the Schedule target, pick AWS Lambda and select the Lambda function created previously. In the Settings step, you can Enable the schedule (so it starts immediately), under "Action after schedule completion" pick `NONE` and disable the Retry policy. Select the option to create a new role for this schedule
    - Lastly, go back to the Lambda function and open its Execution role (there is a hyperlink for it under Configuration > Permissions). Select Add permissions > Attach policies > AmazonEventBridgeSchedulerFullAccess. This will allow the Schedule you created to run the Lambda function
- Deploy the new image to the appropriate lambda function
- Enable EventBridge schedule associated with the lambda function, if it's currently disabled

## (Optional) Configuring Google Sheet and a Google Service Account to write execution results
The app uses [`gspread`](https://docs.gspread.org/en/v6.0.0/) to write execution results to a Google Sheet. Refer to the [library documentation to learn how to setup authentication](https://docs.gspread.org/en/v6.0.0/oauth2.html#for-bots-using-service-account) and let the app write to the spreadsheet.
The spreadsheet to be updated is indicated by its ID configured for the config variable `SPREADSHEET_ID`.
After the authentication is configured as per `gspread` docs, you should have a JSON key file that must be named `keyfile.json` and placed in the root directory of the application.

This configuration is only necessary if you wish to write the results to a Google Sheet to have better visibility on the execution results. The app works just fine without it.

## Next steps / Improvements
- Deploy new image to lambda function via deployment script
- Extend it to work with Immigrant visa appointments
- Use Serverless Framework to facilitate the deployment OR start the Lambda function and EventBridge schedule in the bash script
