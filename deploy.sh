#!/bin/bash

# Check if all mandatory arguments are provided
if [ $# -lt 3 ]; then
    echo "Usage: $0 <account_id> <username> <version> [region]"
    exit 1
fi

# Assign arguments to variables
account_id="$1"
username="$2"
version="$3"
region="${4:-us-east-1}"  # Set default value for region if not provided

echo "Step 1: Building Docker image..."
docker build --platform linux/amd64 -t "$username"/scheduler:"$version" .

echo "Step 2: Authenticating Docker CLI to the Amazon ECR registry..."
aws ecr get-login-password --region "$region" | docker login --username AWS --password-stdin "$account_id".dkr.ecr."$region".amazonaws.com

# echo "Step 3: Creating repository in Amazon ECR..."
# aws ecr create-repository --repository-name "$username"-scheduler --region "$region" --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE

echo "Step 3: Checking if repository already exists in Amazon ECR..."
repository_exists=$(aws ecr describe-repositories --repository-names "$username"-scheduler --region "$region" 2>/dev/null)

if [ -z "$repository_exists" ]; then
    echo "Repository does not exist. Creating repository in Amazon ECR..."
    aws ecr create-repository --repository-name "$username"-scheduler --region "$region" --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
else
    echo "Repository already exists."
fi

echo "Step 4: Tagging local image into Amazon ECR repository as the latest version..."
docker tag "$username"/scheduler:"$version" "$account_id".dkr.ecr."$region".amazonaws.com/"$username"-scheduler:latest

echo "Step 5: Deploying local image to the Amazon ECR repository..."
docker push "$account_id".dkr.ecr."$region".amazonaws.com/"$username"-scheduler:latest

echo "Deployment completed successfully. Please go ahead and update the image in the lambda function."
