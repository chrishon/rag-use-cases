#!/usr/bin/env python3
import os

import aws_cdk as cdk

from bedrock_rag.bedrock_rag_stack import BedrockRagStack
from bedrock_rag.network_stack import NetworkingStack
from bedrock_rag.vectordb_stack import VectorDBStack
from bedrock_rag.s3_knowledgebase_stack import S3Stack


app = cdk.App()
s3Stack = S3Stack(app, "S3Stack")
networkStack = NetworkingStack(app, "NetworkStack")
vectorDBStack = VectorDBStack(app, "VectorDBStack", vpc_id=networkStack.primary_vpc)
BedrockRagStack(
    app,
    "BedrockRagStack",
    vpc_id=networkStack.primary_vpc,
)
app.synth()
