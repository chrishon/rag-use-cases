from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_opensearchservice as opensearch,
    aws_ec2 as ec2,
    Duration,
    # aws_sqs as sqs,
)
from constructs import Construct


class BedrockRagStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc_id: str,
        private_subnet_ids: list,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        llm_handler = lambda_.Function(
            self,
            "LLMHandler",
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="llm_handler.llm_handler",  # Assuming index.py with a function named handler
            code=lambda_.Code.from_asset("bedrock_rag/resources/llm_function"),
            memory_size=256,
            timeout=Duration.seconds(60 * 5),
        )

        llm_handler.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=["arn:aws:bedrock:*::foundation-model/*"],
            )
        )

        ######################################
        ######## Indexing Lambda

        index_handler = lambda_.Function(
            self,
            "RAGIndexHandler",
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="ragindex.indexer",  # Assuming index.py with a function named handler
            code=lambda_.Code.from_asset("bedrock_rag/resources/rag_index"),
            memory_size=256,
            timeout=Duration.seconds(60 * 5),
        )

        index_handler.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    # adapt for s3 & OpenSearch
                ],
                resources=["arn:aws:bedrock:*::foundation-model/*"],
            )
        )
