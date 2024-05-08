#!/bin/bash

# Ask the user for a profile
echo "Enter the AWS profile name:"
read profile_name

echo "Enter the AWS Account ID"
read account_id

echo "Enter the Depoyment Region"
read aws_region

export PROFILE_NAME=$profile_name
export ACCOUNT_ID=$account_id
export AWS_REGION=$aws_region

if [ -z "$profile_name" ]; then
  echo "Profile name cannot be empty."
  exit 1
fi

echo 
read -p "Do you want to use Textract Parsing? (y/n)" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]];
then
   export TEXTRACT_PROCESSING=true
fi

echo 
read -p "Do you want to create new zip files for the Lambda deployment? (Need to choose yes if first-time deployment) (y/n)" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]];
then
   echo "Preparing for deployment, will first run script to package functions for the Lambda deployment..."
   bash ./packager.sh
   # Check if profile name is provided

fi

cd ..
# Execute cdk bootstrap with the provided profile name
cdk bootstrap --profile "$profile_name"
cdk deploy vectorDBServerless --require-approval never
cdk deploy KnowledgeBaseStack --require-approval never
cdk deploy BedrockRagStack --require-approval never

