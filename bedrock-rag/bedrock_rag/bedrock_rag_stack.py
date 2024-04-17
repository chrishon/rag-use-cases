from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_opensearchservice as opensearch,
    aws_ec2 as ec2,
    Duration,
    Fn,
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
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        opensearch_endpoint = Fn.import_value("VectorDB-OpenSearchEndpoint")
        collection_name = Fn.import_value("VectorDB-OpenSearch-CollectionName")
        vector_index_name = None  # TODO Import vector index name here from CFN outputs

        llm_handler = lambda_.Function(
            self,
            "LLMHandler",
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="llm_handler.llm_handler",  # Assuming index.py with a function named handler
            code=lambda_.Code.from_asset("bedrock_rag/resources/llm_function"),
            memory_size=256,
            timeout=Duration.seconds(60 * 5),
            environment={
                "opensearch_endpoint": opensearch_endpoint,
                "vector_index_name": vector_index_name,
            },  # TODO get vector index name
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

        opensearch_collection_access = iam.PolicyDocument(
            actions=[
                "aoss:CreateCollectionItems",
                "aoss:DeleteCollectionItems",
                "aoss:UpdateCollectionItems",
                "aoss:DescribeCollectionItems",
            ],
            resource=f"collection/{collection_name}",
        )
        opensearch_data_access = iam.PolicyDocument(
            actions=[
                "aoss:CreateIndex",
                "aoss:DeleteIndex",
                "aoss:UpdateIndex",
                "aoss:DescribeIndex",
                "aoss:ReadDocument",
                "aoss:WriteDocument",
            ],
            resource=f"index/{collection_name}/*",
        )

        llm_handler.add_to_role_policy(opensearch_collection_access)
        llm_handler.add_to_role_policy(opensearch_data_access)
