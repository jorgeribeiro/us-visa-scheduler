# US Visa Scheduler

## How to run locally
- Install the required python packages: `pip install -r requirements.txt`
- Simply run `python -c "import setup; setup.as_loop()"`

## Next steps
- Test!
- Implement blacklisted dates
- Implement useful email notifications:
    - Successful reschedule
    - Failed login attempt
    - Execution stopped since interview date is nearby
    - Any failures or unexpected results sent to the developer's email
- Provide visibility on the scheduler executions:
    - Google Spreadsheet with a list of the last executions
    - UI that lists the result of the last executions
- Extend it to work with Immigrant visa appointments
- Use Serverless Framework to facilitate the deployment

## Extra notes
```
Upgrading the visa scheduler into a monetized app

Challenges:
1. Must be logged in a user's account to make requests
2. Potential blocks from the API
3. Users need to share their credentials
4. Does being a group processor make it easier to access the API?
5. Testing is challeging since the requests are all live

To solve:
1. Logic to prioritize users who have paid for the service OR run concurrent instances for each user (stop for one week on successful reschedules)?
2. Which user credentials to use for the requests (test if session cookie needs to be match the schedule owner)
3. The appointment request might not work 100% (tests needed)
4. Which DB technology to use
5. Run it as a lambda function

Solution:
1. Use a user's account to make requests
2. Run concurrent instances for each user
3. On successful reschedules, stop for one week

Learnings from latest test (see Latest test below to check the full log):
1. Checking if POST request status code 200 is not 100% accurate. Html page returned contains new schedule date, so that can be compared with the actual date that was requested
  1.1. HTML of the response already captured in response.html
2. SendGrid requests are returning a Forbidden 403 response
```