from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_opensearchservice as opensearch,
    aws_ec2 as ec2,
    Duration,
    Fn,
    aws_apigateway as api,
    # aws_sqs as sqs,
)
from constructs import Construct


class BedrockRagStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        opensearch_endpoint = Fn.import_value("VectorDB-OpenSearchEndpoint")
        collection_name = Fn.import_value("VectorDB-OpenSearch-CollectionName")
        vector_index_name = Fn.import_value(
            "Vector-Index-Name"
        )  # TODO Instead of using outputs, use object references

        llm_handler = lambda_.Function(
            self,
            "LLMHandler",
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="llm_handler.llm_handler",
            code=lambda_.Code.from_asset("bedrock_rag/resources/llm_handler.zip"),
            memory_size=256,
            timeout=Duration.seconds(60 * 5),
            environment={
                "opensearch_endpoint": opensearch_endpoint,
                "vector_index_name": vector_index_name,
            },
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

        opensearch_collection_access = iam.PolicyStatement(
            actions=[
                "aoss:CreateCollectionItems",
                "aoss:DeleteCollectionItems",
                "aoss:UpdateCollectionItems",
                "aoss:DescribeCollectionItems",
            ],
            resources=[f"arn:aws:aoss:*:*:collection/*"],
        )

        opensearch_data_access = iam.PolicyStatement(
            actions=[
                "aoss:CreateIndex",
                "aoss:DeleteIndex",
                "aoss:UpdateIndex",
                "aoss:DescribeIndex",
                "aoss:ReadDocument",
                "aoss:WriteDocument",
            ],
            resources=[f"arn:aws:aoss:*:*:index/*"],
        )

        openseach_api_access = iam.PolicyStatement(
            actions=["aoss:BatchGetCollection", "aoss:APIAccessAll"], resources=["*"]
        )

        bedrock_access = iam.PolicyStatement(
            actions=["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
            resources=["arn:aws:bedrock:*::foundation-model/*"],
        )

        llm_handler.add_to_role_policy(opensearch_collection_access)
        llm_handler.add_to_role_policy(opensearch_data_access)
        llm_handler.add_to_role_policy(opensearch_data_access)
        llm_handler.add_to_role_policy(openseach_api_access)

        query_api = api.LambdaRestApi(self, "Endpoint", handler=llm_handler)
        llm_resource = query_api.root.add_resource("askme")
        llm_resource.add_method("POST")
