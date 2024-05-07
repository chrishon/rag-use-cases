#!/bin/bash

# Ask the user for a profile
echo "Please enter the AWS profile name:"
read profile_name

echo "Preparing for deployment, will first run script to package functions for the Lambda deployment..."
bash ./packager.sh
# Check if profile name is provided
if [ -z "$profile_name" ]; then
  echo "Profile name cannot be empty."
  exit 1
fi
cd ..
# Execute cdk bootstrap with the provided profile name
cdk bootstrap --profile "$profile_name"
cdk deploy vectorDBServerlessStack --require-approval never
cdk deploy KnowledgeBaseStack --require-approval never
cdk deploy BedrockRagStack --require-approval never

