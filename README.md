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

## (Optional) Configuring Google Sheet and a Google Service Account to write execution results
The app uses `gspread` to write execution results to a Google Sheet. Refer to the library documentation to learn how to setup authentication and let the app write to the spreadsheet. 
The spreadsheet to be updated is indicated by its ID configured for the config variable `SPREADSHEET_ID`.
After the authentication is configured as per the instructions provided by the `gspread` docs, you should have a JSON key file that must be named `keyfile.json` and placed in the root directory of the application.

This configuration is only necessary if you wish to write the results to a Google Sheet to have better visibility on the execution results. The app works just fine without it.

## Next steps
- Extend it to work with Immigrant visa appointments
- Update the deployment script to deploy the new image to the Lambda function
- Use Serverless Framework to facilitate the deployment OR start the Lambda function and EventBridge schedule in the bash script
