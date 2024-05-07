#!/usr/bin/env python3
import os

import aws_cdk as cdk

from bedrock_rag_opensearch.bedrock_rag_stack import BedrockRagStack
from bedrock_rag_opensearch.network_stack import NetworkingStack
from bedrock_rag_opensearch.vectordb_stack import VectorDBStack
from bedrock_rag_opensearch.vectordb_serverless_stack import VectorDBServerlessStack

from bedrock_rag_opensearch.s3_knowledgebase_stack import KnowledgeBaseStack

from config.constants import DEFAULT_DEPLOYMENT_REGION, DEFAULT_ACCOUNT
import boto3
import os

iam = boto3.client("iam")
user_arn = iam.get_user()["User"]["Arn"]
use_textract = os.environ.get("TEXTRACT_PROCESSING", False)


app = cdk.App()
env = cdk.Environment(account=DEFAULT_ACCOUNT, region=DEFAULT_DEPLOYMENT_REGION)
vectorDBServerless = VectorDBServerlessStack(
    app, "vectorDBServerless", env=env, user_arn=user_arn
)
s3Stack = KnowledgeBaseStack(
    app, "KnowledgeBaseStack", env=env, use_textract=use_textract
)

bedrockstack = BedrockRagStack(app, "BedrockRagStack", env=env)

# networkStack = NetworkingStack(app, "NetworkStack", env=env)
# vectorDBStack = VectorDBStack(
#     app,
#     "VectorDBStack",
#     vpc=networkStack.primary_vpc,
#     subnets=networkStack.primary_vpc.isolated_subnets,
#     env=env,
# )
app.synth()
