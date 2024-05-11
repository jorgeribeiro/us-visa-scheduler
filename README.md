# US Visa Scheduler

## How to run locally
- Install the required python packages: `pip install -r requirements.txt`
- Simply run `python -c "import setup; setup.as_loop()"`

## How to deploy as a lambda function
- Run `deploy.sh` bash script with the arguments: `account_id`, `username`, `version` and `region` (optional, if not informed value is set to `us-east-1`)
- To successfully run the deployment script, the following must be correctly configured
    - Make sure the script is executable by running `chmod +x deploy.sh`
    - Docker daemon is running
    - AWS credentials are setup for the account ID you're using to deploy the image
- Deploy the new image to the appropriate lambda function

**Missing steps:** Lambda function configuration, EventBridge schedule configuration

## Next steps
- Provide visibility on the scheduler executions:
    - Google Spreadsheet with a list of the last executions
    - UI that lists the result of the last executions
- Extend it to work with Immigrant visa appointments
- Use Serverless Framework to facilitate the deployment
