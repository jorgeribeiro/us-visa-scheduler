# US Visa Scheduler

## How to run locally
- Install the required python packages: `pip install -r requirements.txt`
- Simply run `python -c "import setup; setup.as_loop()"`

## How to deploy as a lambda function
- Build the Docker image:
```
docker build --platform linux/amd64 -t <username>/scheduler:<version> .
```
- Authenticate Docker CLI to the Amazon ECR registry:
```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account_id>.dkr.ecr.us-east-1.amazonaws.com
```
- Create a repository in Amazon ECR (step required only for the first deployment):
```
aws ecr create-repository --repository-name <username>-scheduler --region us-east-1 --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
```
- Tag local image into Amazon ECR repository as the latest version:
```
docker tag <username>/scheduler:<version> <account_id>.dkr.ecr.us-east-1.amazonaws.com/<username>-scheduler:latest
```
- Deploy local image to the Amazon ECR repository:
```
docker push <account_id>.dkr.ecr.us-east-1.amazonaws.com/<username>-scheduler:latest
```

**Missing steps:** Lambda function configuration, EventBridge schedule configuration

## Next steps
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