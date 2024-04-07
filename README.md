# US Visa Scheduler

## How to run locally
- Install the required python packages: `pip install -r requirements.txt`
- Simply run `python -c "import setup; setup.as_loop()"`

## Next steps
- Confirm successful reschedule by checking response's HTML
- Implement delayed retry for lambda function
- Stop execution 7 days before the current interview date
- Implement useful email notifications:
    - Successful reschedule
    - Any failures or unexpected results sent to the developer's email
- Test!