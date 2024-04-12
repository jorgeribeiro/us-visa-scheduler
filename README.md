# US Visa Scheduler

## How to run locally
- Install the required python packages: `pip install -r requirements.txt`
- Simply run `python -c "import setup; setup.as_loop()"`

## Next steps
- Implement useful email notifications:
    - Execution stopped since interview date is nearby
    - Any failures or unexpected results sent to the developer's email
- Provide visibility on the scheduler executions:
    - Google Spreadsheet with a list of the last executions
    - UI that lists the result of the last executions
- Extend it to work with Immigrant visa appointments
- Use Serverless Framework to facilitate the deployment

## Extra notes
Challenges:
1. Must be logged in a user's account to make requests
2. Potential blocks from the API
3. Users need to share their credentials
4. Testing is challeging since the requests are all live

Solution:
1. Run concurrent instances for each user
2. On successful reschedules, stop for one week